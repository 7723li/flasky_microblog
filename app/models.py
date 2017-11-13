#Werkzeug 中的 security 模块能够很方便地实现密码散列值的计算#generate_password_hash(password, method=pbkdf2:sha1, salt_length=8)：这个函数将
#原始密码作为输入，以字符串形式输出密码的散列值， 输出的值可保存在用户数据库中。
#method 和 salt_length 的默认值就能满足大多数需求。
#check_password_hash(hash, password)：这个函数的参数是从数据库中取回的密码散列
#值和用户输入的密码。返回值为 True 表明密码正确。
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin,AnonymousUserMixin
#TimedJSONWebSignatureSerializer 类生成具有过期时间的 JSON Web 签名
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, url_for
from datetime import datetime
from . import login_manager,db
import hashlib, os, sys
#=====forgery_py=====
#若想实现博客文章分页，我们需要一个包含大量数据的测试数据库。手动添加数据库记录
#浪费时间而且很麻烦， 所以最好能使用自动化方案。有多个 Python 包可用于生成虚拟信
#息，其中功能相对完善的是 ForgeryPy
from markdown import markdown
from app.exceptions import ValidationError
import bleach

#关注关联表的模型实现
class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

#表9-1　程序的权限
#操　　作               位　　值            说　　明

#关注用户               0b00000001（ 0x01） 关注其他用户
#在他人的文章中发表评论 0b00000010（ 0x02） 在他人撰写的文章中发布评论
#写文章                 0b00000100（ 0x04） 写原创文章
#管理他人发表的评论     0b00001000（ 0x08） 查处他人发表的不当评论
#管理员权限             0b10000000（ 0x80） 管理网站
class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

#表9-2　用户角色
#用户角色                权　　限           说　　明
    
#匿名                   0b00000000（ 0x00） 未登录的用户。在程序中只有阅读权限
#用户                   0b00000111（ 0x07） 具有发布文章、发表评论和关注其他用户的权限。这是新用户的默认角色
#协管员                 0b00001111（ 0x0f） 增加审查不当评论的权限
#管理员                 0b11111111（ 0xff） 具有所有权限，包括修改其他用户所属角色的权限
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    #默认是否具有该角色的权限
    default = db.Column(db.Boolean, default=False, index=True)
    #表示位标志
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')#一对多->一个角色对应多个用户
    #拥有方法append，即可执行Role.append(x)
    
#insert_roles() 函数并不直接创建新角色对象，而是通过角色名查找现有的角色，然后再
#进行更新，只有当数据库中没有某个角色名时才会创建新角色对象
#只有在有新角色是才调用此函数，因此一般不在程序中调用，而是在shell中调用
    @staticmethod
    def insert_roles():
        roles = {
            #进行"与"运算求出角色权限
#匿名角色不需要在数据库中表示出来，这个角色的作用就是为了表示不在数据库中的用户
            'User':(Permission.FOLLOW |
                    Permission.COMMENT |
                    Permission.WRITE_ARTICLES, True),
            'Moderator':(Permission.FOLLOW |
                        Permission.COMMENT |
                        Permission.WRITE_ARTICLES |
                        Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name

#FlaskLogin 提供了一个 UserMixin 类，其中包含
#这些方法(is_authenticated等四个)的默认实现
class User(UserMixin,db.Model):
    __tablename__ = 'users'
    #关键信息
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    avatar_hash = db.Column(db.String(32))
    have_avatar = db.Column(db.Boolean())
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)#是否已认证，只在注册时使用一次
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    
    #个人信息
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')#一对多->一个用户对应多篇文章
    
    #followed自己关注别人，followers自己被比人关注
    #使用两个一对多关系实现的多对多关系,followed 和 followers 关系都定义为单独的一对多关系
    followed = db.relationship('Follow',
                               #关注的外键是Follow中的关注者(即自己)id
                        foreign_keys=[Follow.follower_id],
                               #joined模式可以实现立即从联结查询中加载相关对象
                               #例如，如果某个用户关注了 100 个用户，调用 user.followed.all() 后会返回一个列
                               #表，其中包含 100 个 Follow 实例，每一个实例的 follower 和 followed
                               #回引属性都指向相应的用户
                #db.backref() 参数并不是指定这两个关系之间的引用关系，而是回引 Follow 模型。
                        backref=db.backref('follower', lazy='joined'),#('follower', {'lazy': 'joined'})
                        lazy='dynamic',
                        cascade='all, delete-orphan')
    
    followers = db.relationship('Follow',
                                #关注者的外键是Follow中的关注者们的id
                        foreign_keys=[Follow.followed_id],
                #反回引一个follower(followed)到Follow模型，follower(关注者)关联外键followed_id(关注者的id)
                #此处这个一对多关系即一个用户对应多个关注者
                #以上一个是一个用户关注对应多个自己的关注
                        backref=db.backref('followed', lazy='joined'),
                        lazy='dynamic',
                        cascade='all, delete-orphan')

    #users 和 posts 表与 comments 表之间的一对多关系
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    #follow() 方法手动把 Follow 实例插入关联表，从而把关注者和被关注者联接起来
    def follow(self, user):
        if not self.is_following(user):
                    # follower_id->self.id,followed_id->user.id
            f = Follow(follower=self, followed=user)
            db.session.add(f)
            
    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
   
    #定义默认的用户角色f
    def __init__(self, **kwargs):
        #以kwargs为参数调用父类中的__init__初始化函数
        #可避免“反复调用父类”的错误
        #User 类的构造函数首先调用基类的构造函数，如果创建基类对象后还没定义角色，则根据
        #电子邮件地址决定将其设为管理员还是默认角色。
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            #如果邮箱不为管理员邮箱，则默认为普通用户
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

        #若邮箱不为空且邮箱MD5 散列值不为空
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

        #设置自己关注自己
        self.follow(self)
        
    def __repr__(self):
        return '<User %r>' % self.username

    #如果角色中包含请求的所有权限位， 则返回 True，表示允许用户执行此项操作
    #代入参数为需要检测是否符合的身份
    def can(self, permissions):
        #管理员0xff 与运算 任何数均等于另外一个值
        return self.role is not None and (self.role.permissions & permissions) == permissions

    #检查管理员权限的功能经常用到，因此使用单独的方法 is_administrator() 实现。
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    #添加Gravatar（ http://gravatar.com/提供的用户头像
    #生成 Gravatar URL
    def gravatar(self, size=100, default='identicon', rating='g'):
        # if request.is_secure:
        #     url = 'https://secure.gravatar.com/avatar'
        # else:
        #     url = 'http://www.gravatar.com/avatar'
        # #从数据库缓存中取出散列值
        # hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        # return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
        #     url=url, hash=hash, size=size, default=default, rating=rating)
        
        #使用本地缓存头像
        if self.have_avatar:
            return url_for('static',filename='Gravatar/{}.jpg'.format(self.username))
        return url_for('static',filename='Gravatar/default.jpg')
         
    @staticmethod
    def download_all_avatars(size=512, default='identicon', rating='g', username=None):
        import requests
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        if username == None:
            for u in User.query.all():
                hash = u.avatar_hash or hashlib.md5(u.email.encode('utf-8')).hexdigest()
                avatar_url='{url}/{hash}?s={size}&d={default}&r={rating}'.format(
                    url=url, hash=hash, size=size, default=default, rating=rating)
                pic=requests.get(avatar_url).content
                with open(current_app.config['UPLOADED_PHOTOS_DEST']+'/'+u.username+'.jpg','wb') as f:
                    f.write(pic)
        else:
                u=User.query.filter_by(username=username).first()
                hash = u.avatar_hash or hashlib.md5(u.email.encode('utf-8')).hexdigest()
                avatar_url='{url}/{hash}?s={size}&d={default}&r={rating}'.format(
                    url=url, hash=hash, size=size, default=default, rating=rating)
                pic=requests.get(avatar_url).content
                with open(current_app.config['UPLOADED_PHOTOS_DEST']+'/'+u.username+'.jpg','wb') as f:
                    f.write(pic)

    def is_following(self, user):
        #此处关联外键未follower_id,即follower_id为self.id
        return self.followed.filter_by(followed_id=user.id).first() is not None
    
    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    #获取所关注用户的文章
    #联结关注者是自己的结果和被关注者的id结果得出自己关注的作者的文章
    @property
    def followed_posts(self):
        #return Post.query.join(Follow,\
        #                       Follow.followed_id ==Post.author_id).filter(Follow.follower_id == self.id)
                               #获得同时有发过文章和被关注的用户        #过滤出其中被自己关注的用户      
                               #联结得出被自己关注的用户发过的文章

        #这样比较好理解，先选出自己的关注用户，再在其中过滤出发过文章的.
        return Post.query.join(Follow,\
                               Follow.follower_id==self.id).filter(Follow.followed_id ==Post.author_id)

    #c=Post.query.join(Follow,Follow.follower_id==self.id)
    #cc=Post.query.all()
    #cc=c.all()
    
    #使已存在的用户关注自己
    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    #把用户转换成 JSON 格式的序列化字典
    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', id=self.id, _external=True),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts': url_for('api.get_user_posts', id=self.id, _external=True),
            'followed_posts': url_for('api.get_user_followed_posts',
            id=self.id, _external=True),
            'post_count': self.posts.count()
        }
        return json_user
    
    #生成虚拟用户
    @staticmethod
    def generate_fake(count=100):
        #若发生随机生成的邮件地址和用户名与数据库中已存在的产生重复，则会抛出IntegrityError异常
        from sqlalchemy.exc import IntegrityError#Integrity完整性
        from random import seed
        import forgery_py

        seed()
        #使用ForgeryPy模块随机生成一百个合法的账户并注册到数据库中，作测试用
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                        username=forgery_py.internet.user_name(True),
                        #password=forgery_py.lorem_ipsum.word(),
                        password='123',
                        confirmed=True,
                        name=forgery_py.name.full_name(),
                        location=forgery_py.address.city(),
                        about_me=forgery_py.lorem_ipsum.sentence(),
                        member_since=forgery_py.date.date(True))
            db.session.add(u)

            try:
                db.session.commit()
            except IntegrityError:
                #在继续操作之前回滚会话,在循环中生成重复内容时不会把用户写入数据库，
                #因此生成的虚拟用户总数可能会比预期少。
                db.session.rollback()

    #generate_confirmation_token() 方法生成一个令牌，有效期默认为一小时
    #dumps() 方法为指定的数据生成一个加密签名，然后再对数据和签名进行序列化，
    #生成令牌字符串
    #目的是的使用id发送确认邮件
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    #confirm() 方法检验令牌，如果检验通过，则把新添加的 confirmed 属性设为 True。
    #除了检验令牌， confirm() 方法还检查令牌中的 id 是否和存储在 current_user 中的已登录
    #用户匹配。如此一来，即使恶意用户知道如何生成签名令牌，也无法确认别人的账户。
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        
        if data.get('confirm') != self.id:
            return False
        
        self.confirmed = True
        db.session.add(self)
        return True

    #生成重置密码时的令牌
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    #支持基于令牌的认证
    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        #如果更改的邮箱已被占用
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        #重新计算散列值
        self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    #刷新用户的最后访问时间
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

#匿名用户模型，注意方法必须和User模型中对应的一样
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False    

    def is_administrator(self):
        return False

#设为用户未登录时current_user(anonymous_user匿名用户) 的值
login_manager.anonymous_user = AnonymousUser

#文章模型
#博客文章包含正文、时间戳以及和 User 模型之间的一对多关系
class Post(db.Model):
    __searchable__ = ['body']
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    #users 和 posts 表与 comments 表之间的一对多关系
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    #把文章转换成 JSON 格式的序列化字典
    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id, _external=True),
            'comments': url_for('api.get_post_comments', id=self.id, _external=True),
            'comment_count': self.comments.count()
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        
        return Post(body=body)

    #生成虚拟博客文章
    @staticmethod
    def generate_fake(count=300):
        from random import seed, randint
        import forgery_py
        seed()
        #用户总数
        user_count = User.query.count()
        for i in range(count):
            # offset() 查询过滤器,这个过滤器会跳过参数中指定的记录数量
            #通过设定一个随机的偏移值，再调用 first()方法，就能每次都获得一个不同的随机用户
            #通过抽取随机用户生成共100篇文章，因此最后结果有些用户会有几篇而有些会没有
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                        timestamp=forgery_py.date.date(True),
                        author=u)
            db.session.add(p)
            db.session.commit()

    #在 Post 模型中处理 Markdown 文本
    #on_changed_body 函数把 body 字段中的文本渲染成 HTML 格式，
    #结果保存在 body_html 中，自动且高效地完成Markdown 文本到 HTML 的转换。
    @staticmethod
                        #Post   body
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']

        #3.转换的最后一步由linkify()函数完成，这个函数由Bleach提供，把纯文本中的URL转换成适当的<a>链接
                                                #2.clean() 函数删除所有不在白名单中的标签
        target.body_html = bleach.linkify(bleach.clean
                                          #1.把 Markdown 文本转换成 HTML
                                          (markdown(value,output_format='html'),
                                           tags=allowed_tags,strip=True))
        
#on_changed_body 函数注册在 body 字段上，是 SQLAlchemy“ set”事件的监听程序，这意
#味着只要这个类实例的 body 字段设了新值，函数就会自动被调用
db.event.listen(Post.body, 'set', Post.on_changed_body)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def to_json(self):
        json_user = {
            'url': url_for('api.get_post_comments', id=self.id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'disabled': self.disabled,
            'author_url': url_for('api.get_user',id=self.author_id, _external=True),
            'post_url': url_for('api.get_post',id=self.post_id, _external=True)
        }
        return json_user
    
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i','strong']
        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'),
                                                       tags=allowed_tags, strip=True))

#在修改 body 字段内容时触发，自动把 Markdown 文本转换成 HTML。
db.event.listen(Comment.body, 'set', Comment.on_changed_body)

@login_manager.user_loader#加载用户的回调函数
def load_user(user_id):
    return User.query.get(int(user_id))
#如果能找到用户，这个函数必须返回用户对象；否则应该返回 None。
