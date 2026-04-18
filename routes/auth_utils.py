import os
from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_email = os.getenv('EMAIL_ADMIN')
        
        if not current_user.is_authenticated or current_user.email != admin_email:
            abort(403)
            
        return f(*args, **kwargs)
    return decorated_function