from flask import current_app
from flask_wtf import FlaskForm
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf.file import FileField, FileRequired, FileAllowed
#• PageDown： 使用 JavaScript 实现的客户端 Markdown 到 HTML 的转换程序。
#• Flask-PageDown： 为 Flask 包装的 PageDown，把PageDown集成到Flask-WTF表单中。
#• Markdown： 使用 Python 实现的服务器端 Markdown 到 HTML 的转换程序。
#• Bleach： 使用 Python 实现的 HTML 清理器。
from flask_pagedown.fields import PageDownField
from wtforms import StringField, SubmitField, TextAreaField, SelectField, BooleanField
from wtforms import ValidationError
from wtforms.validators import Required, Length, Email, Regexp
from ..models import Role, User, Comment

photos = UploadSet('photos',IMAGES)

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

#普通用户资料编辑表单
class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

#管理员使用的资料编辑表单
class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64),Email()])
    username = StringField('Username', \
                validators=[Required(), Length(1, 64),
                            Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                            'Usernames must have only letters, '
                            'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    # 元组中的标识符是角色的 id，因为这是个整数，
    #所以在 SelectField 构造函数中添加 coerce=int 参数，从而把字段的值转换为整数，
    #而不使用默认的字符串。
    #表单提交后， id 从字段的 data 属性中提取，并且查询时会
    #使用提取出来的 id 值加载角色对象
    #coerce:逼迫;威胁;强迫，强制;控制，限制
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')
    
    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices =[]
        #罗列出Role中所有角色名，并提供给SelectField
        #选项的标识符和显示在控件中的文本字符串
        #[(2, 'Administrator'), (3, 'Moderator'), (1, 'User')]
        for role in Role.query.order_by(Role.name).all():
            self.role.choices.append((role.id, role.name))
            
        self.user = user

    #首先要检查字段的值是否发生了变化，如果有变化（即可改变该用户的email地址和用户名），就要保证新值不
    #和其他用户的相应字段值重复； 如果字段值没有变化，则应该跳过验证
    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
        
    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

#博客文章表单
class PostForm(FlaskForm):
    #body = TextAreaField("What's on your mind?", validators=[Required()])
    #启用 Markdown 的文章表单
    #即可使用markdowm语法，不再是纯文本
    body = PageDownField("What's on your mind?", validators=[Required()])
    submit = SubmitField('Submit')

class CommentForm(FlaskForm):
    body = StringField('Enter your comment', validators=[Required()])
    submit = SubmitField('Submit')

class UploadForm(FlaskForm):
    photo = FileField(validators=[FileAllowed(photos,u'只能上传图片哦!'),
                                  FileRequired(u'文件为选择!')])
    submit = SubmitField(u'上传')