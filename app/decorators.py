from functools import wraps

from flask import abort
from flask_login import current_user


def superuser_check(user):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if user.is_superuser == False:
                abort(404)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
