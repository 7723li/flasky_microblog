#程序包的构造文件
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown
from config import config

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()

login_manager = LoginManager()
#LoginManager 对象的 session_protection 属性可以设为 None、 'basic' 或 'strong'，以提
#供不同的安全等级防止用户会话遭篡改。 设为 'strong' 时， Flask-Login 会记录客户端 IP
#地址和浏览器的用户代理信息， 如果发现异动就登出用户
login_manager.session_protection = 'strong'
#login_view 属性设置登录页面的端点,用于login_required修饰器发往登陆页面
login_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app_1(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    from .main import main as main_blueprint
    from .auth import auth as auth_blueprint
    from .api_1_0 import api as api_1_0_blueprint
    
    app.register_blueprint(main_blueprint)#注册蓝本
#注册蓝本时使用的 url_prefix 是可选参数。如果使用了这个参数，注册后蓝本中定义的
#所有路由都会加上指定的前缀， 即这个例子中的 /auth。例如， /login 路由会注册成 /auth/
#login，在开发 Web 服务器中，完整的 URL 就变成了 http://localhost:5000/auth/login。
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

    return app

