from . import api
from .errors import unauthorized, bad_request, forbidden, validation_error
from ..models import User, AnonymousUser
# Flask 的全局对象 g 
from flask import g
from flask_httpauth import HTTPBasicAuth

#创建一个 HTTPBasicAuth 类对象
auth = HTTPBasicAuth()

#支持令牌的改进验证回调
#如果认证密令不正确，服务器向客户端返回 401 错误。默认情况下，
#Flask-HTTPAuth 自动生成这个状态码
@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    
    user = User.query.filter_by(email = email).first()
    if not user:
        return False

    #验证回调函数把通过认证的用户保存在 Flask 的全局对象 g 中
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)

#自定义这个错误响应
@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')

@api.before_request
@auth.login_required
def before_request():
    #拒绝已通过认证但没有确认账户的用户
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return forbidden('Unconfirmed account')

#生成认证令牌
@api.route('/token')
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(
        expiration=3600), 'expiration': 3600})
