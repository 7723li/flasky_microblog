#检查用户权限的自定义修饰器
#让视图函数只对具有特定权限的用户开放
from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission

#func
#<function for_admins_only at 0x02A60198>
#<function for_moderators_only at 0x02A60300>
def permission_required(permission):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                #用户不具有指定权限，则返回 403 错误码，即 HTTP“禁止”错误
                abort(403)
            #如果用户拥有权限，则执行调入的函数（即可返回一个模板）
            return func(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(func):
    return permission_required(Permission.ADMINISTER)(func)

#>>> def a(num):
#        def b(func):
#                def c():
#                        if num>1:
#                                return 2
#                        return func()
#                return c
#        return b

#>>> @a(5)
#def d():
#        return 1
#同理于a(5)(d())()

#>>> f=d()
#>>> f
#2
#>>> @a(1)
#def d():
#        return 1

#>>> f=d()
#>>> f
#1
#>>> def g(func):
#    return a(5)(func)

#>>> @g
#def d():
#        return 1

#>>> f=d()
#>>> f
#2
#>>> 
