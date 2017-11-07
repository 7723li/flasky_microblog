from functools import wraps
from flask import g
from .errors import unauthorized, bad_request, forbidden, validation_error

def permission_required(permission):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			if not g.current_user.can(permission):
				return forbidden('Insufficient permissions')
		return f(*args, **kwargs)
	return decorated_function
return decorator