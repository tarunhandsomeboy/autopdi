from functools import wraps
from flask import session, request, redirect, url_for, jsonify, g
from models.user import User

def login_user(user: User):
    """Sets user session securely."""
    session['user_id'] = user.id
    session['user_role'] = user.role
    session['user_name'] = user.name
    session['user_email'] = user.email
    session.permanent = True


def logout_user():
    """Clears user session."""
    session.clear()


def get_current_user():
    """Retrieves current logged-in user from session."""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


def login_required(f):
    """Decorator ensuring a user is authenticated."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': 'Authentication required. Please log in.'}), 401
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """Decorator ensuring current user has one of the allowed roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                if request.path.startswith('/api/'):
                    return jsonify({'success': False, 'message': 'Authentication required.'}), 401
                return redirect(url_for('auth.login', next=request.url))

            user_role = session.get('user_role')
            if user_role not in roles:
                if request.path.startswith('/api/'):
                    return jsonify({'success': False, 'message': 'Access forbidden: Insufficient permissions.'}), 403
                
                # Redirect to user's proper dashboard based on actual role
                if user_role == 'CUSTOMER':
                    return redirect(url_for('customer.dashboard'))
                elif user_role == 'INSPECTOR':
                    return redirect(url_for('inspector.dashboard'))
                elif user_role == 'ADMIN':
                    return redirect(url_for('admin.dashboard'))
                return redirect(url_for('auth.login'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator
