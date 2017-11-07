from flask import render_template,redirect,request,url_for,flash
from flask_login import login_user,logout_user,login_required,current_user
from . import auth
from .forms import LoginForm,RegistrationForm,ChangePasswordForm,\
     PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm
from ..models import User
from .. import db
from ..email import send_email

@auth.route('/login',methods=['GET', 'POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        #使用email登录
        user = User.query.filter_by(email=form.email.data).first()
        #用户存在切密码正确
        if user is not None and user.verify_password(form.password.data):
            #改变current_user
            login_user(user, form.remember_me.data)
#用户访问未授权的 URL 时会显示登录表单，
#Flask-Login会把原地址保存在查询字符串的 next 参数中，这个参数可从 request.args 字典中读取。
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    #print(form.csrf_token)
    form.email.data='li542131220@163.com'
    return render_template('auth/login.html',form=form,token=form.csrf_token)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/register',methods=['GET', 'POST'])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        user=User(email=form.email.data,
                  username=form.username.data,
                  password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()#令牌
        send_email(user.email,
                   'Confirm Your Account',
                   'auth/email/confirm',
                   user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html',form=form)

#钩子
#before_first_request：注册一个函数，在处理第一个请求之前运行。
#before_request：注册一个函数，在每次请求之前运行。
#after_request：注册一个函数，如果没有未处理的异常抛出，在每次请求之后运行。
#teardown_request：注册一个函数，即使有未处理的异常抛出，也在每次请求之后运行。
#允许未确认的用户登录，但只显示一个页面，这个页面要求用户在获取权限之前先确认账户
#在 before_app_request 处理程序中过滤未确认的账户
@auth.before_app_request
def before_request():
    print(request.endpoint)
    #用户已登录
    #用户的账户还未确认
    #请求的端点不在认证蓝本中（即在主页蓝本或其他中）
    #如果请求满足以上 3 个条件， 则会被重定向到 /auth/unconfirmed 路由
    #(注册成功后请求节点为mian.index)
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth.'\
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))

#注册成功之后未认证而尝试登录
@auth.route('/unconfirmed')
def unconfirmed():
    #anonymous匿名
    #若当前用户未登录(即注册并尝试登录成功后又登出)或已认证
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

#这个函数先检查已登录的用户是否已经确认过， 如果确认过，则重定向到首页，因为很
#显然此时不用做什么操作。 这样处理可以避免用户不小心多次点击确认令牌带来的额外工作。
#注册-->邮件点击链接/confirm/<token>-->发往登录页面登录-->登录成功显示flash-->重定向到主页
#发送至邮件的认证链接
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    #User实例中的confirmed列对应的参数
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    #User中的confirmed方法(例，current_user为asd)
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

#重新发送账户确认邮件
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email,
               'Confirm Your Account',
               'auth/email/confirm',
               user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

#登录后更改密码
@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        #输入的旧密码正确则修改为输入的新密码
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('Your password has been updated.')
            #安全起见，更改密码后需退出重新登录
            logout_user()
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)

#忘记密码重置密码,此函数主要用于验证用户邮箱并发送使用重置令牌的重置链接至该邮箱，确保密码的安全性
@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    #若当前用户不为匿名, 也就是已登陆的用户,即已记起密码，无需重置
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    #只有一个填写email的输入框，用于输入登陆用的email
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()#注意confirm与reset的区别
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token,)
                       #next=request.args.get('next'))
            flash('An email with instructions to reset your password has been '
                  'sent to you.')
        else:
            flash('没有找到该邮件的注册用户')
            return render_template('auth/reset_password.html', form=form)
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html',form=form)

#用于重置密码
@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('邮件地址输入错误')
            return redirect(url_for('auth.password_reset',token=token))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            flash('Sonething is WRONG')
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html',form=form)

#改变邮件地址
@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        #密码正确
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)

@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))

#login_required 修饰器
#如果未认证的用户访问这个路由， Flask-Login 会拦截请求，把用户发往登录页面。
@auth.route('/secret')
@login_required
def secret():
    return '<a href="/">Only authenticated users are allowed!</a>'
