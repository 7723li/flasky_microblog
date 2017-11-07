#创建认证蓝本
#对于不同的程序功能，我们要使用不同的蓝本，这是保持代码整齐有序的好方法。
from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views
