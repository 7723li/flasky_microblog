from flask import render_template, flash, redirect, url_for, abort, request, current_app, make_response, Response, session
from flask_login import login_required, current_user
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm, UploadForm, photos
from .. import db
from ..decorators import admin_required, permission_required
from ..models import Permission, User, Role, Post, Comment
from .. import login_manager
from ..camera import VideoCamera
import os, json, subprocess, re, time, socket

@main.route('/', methods=['GET', 'POST'])
@main.route('/index', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        #单篇文章
        #以字符类返回pagedowm输入框中的数据
        post = Post(body=form.body.data,
                    #作者为当前用户
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('main.index'))

    #每次进入默认为显示全部文章
    show_followed = False
    
    if current_user.is_authenticated:
        #show_followed
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query

    #渲染的页数从请求的查询字符串（ request.args）中获取，如果没有明确指定，则默认渲
    #染第一页。参数 type=int 保证参数无法转换成整数时，返回默认值。
    page = request.args.get('page', 1, type=int)
    #分页对象
    #iter_pages(left_edge=2,left_current=2,right_current=5,right_edge=2)
    #一个迭代器，返回一个在分页导航中显示的页数列表。这个列表的最左边显示 left_
    #edge 页，当前页的左边显示 left_current 页，当前页的右边显示 right_current 页，
    #最右边显示 right_edge 页。例如，在一个 100 页的列表中，当前页为第 50 页，使用
    #默认配置，这个方法会返回以下页数： 1、 2、 None、 48、 49、 50、 51、 52、 53、 54、
    #55、 None、 99、 100。 None 表示页数之间的间隔(应用于_marcos.html中)
    #prev() 上一页的分页对象
    #next() 下一页的分页对象
            #timestamp时间戳
            #desc降序
    pagination = query.order_by(Post.timestamp.desc()).paginate(
                        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)
                        #页数
                        #可选参数 per_page 用来指定每页显示的记录数量； 如果没有指定，
                            #则默认显示 20 个记录（指定默认10）
                        #设为 False，页数超出范围时会返回一个空列表
    posts = pagination.items

    a = subprocess.getoutput('python3 DHT11.py')
    b = re.findall('不是内部或外部命令',a)
    if(b != []):
        a = subprocess.getoutput('python DHT11.py')
        b = re.findall("No module named '(.*?)'",a)
        if(b != []):
            a = '{"tempture": "Null", "humidity": "Null"}'

    local_ip_add = socket.gethostbyname(socket.gethostname())
    return render_template('index.html',form=form, posts=posts ,\
                           pagination=pagination,
                           show_followed=show_followed,a=json.loads(a),
                           local_ip_add = local_ip_add)

#查询所有文章
@main.route('/all')
@login_required
def show_all():
    #cookie 只能在响应对象中设置，因此这两个路由不能依赖 Flask，要使用make_response()方法创建响应对象
    resp = make_response(redirect(url_for('.index')))
    #可选的 max_age 参数设置 cookie 的过期时间，单位为秒
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp

#所关注用户的文章
@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp

@main.route('/userlist',methods=['GET', 'POST'])
@login_required
@admin_required
def userlist():
    userlist=User.query.all()
    return render_template('userlist.html',userlist=userlist)

@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    num=len(Post.query.filter_by(author_id=current_user.id).all())
    return render_template('user.html', user=user, posts=posts, num=num)

#资料编辑路由
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('main.user', username=current_user.username))
    #自动插入定义好的数据
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

#管理员的资料编辑路由
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    #Flask-SQLAlchemy 提供的 get_or_404() 函数，如果提供的 id不正确，则会返回 404 错误。
    user = User.query.get_or_404(id)
    #print(user)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)

#文章的固定链接
@main.route('/post/<int:id>', methods=['GET', 'POST'])
@login_required
def post(id):
    #只取出单篇文章
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('Your comment has been published.')
        #url_for() 函数的参数中把 page 设为 -1，这是个特殊的页数，用来请求评论的最后一页
        #所以刚提交的评论才会出现在页面中
        return redirect(url_for('main.post', id=post.id, page=-1))
    
    page = request.args.get('page', 1, type=int)
    
    if page == -1:
        page = (post.comments.count() - 1)/current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
        
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    moderate=False
    if current_user.can(Permission.MODERATE_COMMENTS):
        moderate=True
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination,
                           moderate=moderate)

#编辑博客文章的路由
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    print(User.query.get_or_404(post.author_id).role_id)
    #尽管页面中禁用了编辑入口，也避免非管理员用户或非作者本人直接输入/edit/<int:id>进入编辑界面
    if current_user != post.author and not current_user.can(Permission.MODERATE_COMMENTS):
        abort(403)
        
    if not current_user.can(Permission.ADMINISTER) and \
                   User.query.get_or_404(post.author_id).role_id==2:
        abort(403)
            
    form = PostForm()
    if form.validate_on_submit():
        #更新markdown原文
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)

@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('.user', username=username))


#自己的粉丝
@main.route('/followers/<username>')
@login_required
def followers(username):
    #取出需查询的用户
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


#自己关注别
@main.route('/followed-by/<username>')
@login_required
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)

#管理评论
@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    #按时间罗列出所有评论
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)

@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    if not current_user.can(Permission.ADMINISTER) and \
                   User.query.get_or_404(comment.author_id).role_id==2:
        return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))

@main.route('/video')
@login_required
def video():
    return Response(video_gen(VideoCamera()),
        mimetype='multipart/x-mixed-replace; boundary=frame')

def video_gen(camera):
    while True:
        frame=camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')  

@main.route('/upload',methods=['GET', 'POST'])
@login_required
def upload():
    form=UploadForm()
    if form.validate_on_submit():
        filename=current_user.username
        with open(current_app.config['UPLOADED_PHOTOS_DEST']+'\\'+filename+'.jpg','wb') as p:
            p.write(form.photo.data.read())
        current_user.have_avatar=True
        db.session.add(current_user)
        db.session.commit()
        flash('你的头像已经更新.')
        return redirect(url_for('main.upload'))
    return render_template('upload.html',form=form,current_app=current_app)  

@main.route('/control',methods=['GET','POST'])
@login_required
def control(direction='none'):
    return render_template('control.html',direction=direction)

@main.route('/control/<direction>',methods=['GET','POST'])
@login_required
def _control(direction='none'):
    return render_template('control.html',direction=direction)

def start_up_craweler():
    CrawlerPath = os.path.abspath(os.path.dirname(__file__)) + '\\baiduAip\\MoJiWeather.py'
    CrawlerPath = CrawlerPath.replace('main', 'static')
    WeatherMessage = subprocess.getoutput("python {}" . format(CrawlerPath))
    return WeatherMessage

@main.route('/weather', methods=['GET', 'POST'])
@login_required
def weather():
    try:
        t = session['weather_time']
    except:
        t = None
        session['weather_time'] = time.time()

    if t == None:
        WeatherMessage = start_up_craweler()
        session['WeatherMessage'] = WeatherMessage
    else:
        if time.time() - t >= 3600:
            session['weather_time'] = time.time()
            WeatherMessage = start_up_craweler()
            session['WeatherMessage'] = WeatherMessage
        else:
            try:
                WeatherMessage = session['WeatherMessage']
            except:
                WeatherMessage = start_up_craweler()
                session['WeatherMessage'] = WeatherMessage

    Mp3Path = url_for('static', filename = 'baiduAip/temp.mp3')
    return render_template('weather.html',
        WeatherMessage = WeatherMessage, Mp3Path = Mp3Path)

@main.route('/api_list')
@login_required
def api_list():
    postid=Post.query.filter_by(author_id=current_user.id).all()[0].id
    return render_template('api_list.html',postid=postid)

@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "For administrators!"
