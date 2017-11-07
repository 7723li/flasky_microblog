#创建蓝本
from flask import Blueprint

main = Blueprint('main', __name__)#蓝本的名字和蓝本所在的包或模块

#避免循环导入依赖，因为在views.py 和 errors.py 中还要导入蓝本 main。
from . import views, errors
from ..models import Permission

# Permission 类为所有位定义了常量以便于获取
#把 Permission 类加入模板上下文
#上下文处理器能让变量在所有模板中全局可访问
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
