"""
Authentication and User Management System
Add this as auth.py in your project root
"""

from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
from datetime import datetime

# ================= USER MODEL =================

class User(UserMixin):
    """User model for Flask-Login"""
    
    def __init__(self, id, username, email, role='user', created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.role = role
        self.created_at = created_at or datetime.now()
    
    def has_permission(self, permission):
        """Check if user has specific permission"""
        permissions = {
            'admin': ['read', 'write', 'delete', 'manage_users', 'view_all'],
            'user': ['read', 'write'],
            'viewer': ['read']
        }
        return permission in permissions.get(self.role, [])
    
    def can_access_document(self, document_path, db):
        """Check if user can access a specific document"""
        cursor = db.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM document_access 
            WHERE user_id = ? AND document_path = ?
        """, (self.id, document_path))
        
        has_direct_access = cursor.fetchone()[0] > 0
        
        # Admins can access everything
        if self.role == 'admin':
            return True
        
        # Check if document is in user's folder
        if document_path.startswith(f'uploaded_docs/{self.username}/'):
            return True
        
        # Check explicit access grants
        return has_direct_access
    
    @staticmethod
    def get(user_id, db):
        """Load user from database"""
        cursor = db.cursor()
        cursor.execute("""
            SELECT id, username, email, role, created_at 
            FROM users WHERE id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        if row:
            return User(row[0], row[1], row[2], row[3], row[4])
        return None
    
    @staticmethod
    def get_by_username(username, db):
        """Load user by username"""
        cursor = db.cursor()
        cursor.execute("""
            SELECT id, username, email, role, created_at 
            FROM users WHERE username = ?
        """, (username,))
        
        row = cursor.fetchone()
        if row:
            return User(row[0], row[1], row[2], row[3], row[4])
        return None
    
    @staticmethod
    def authenticate(username, password, db):
        """Authenticate user with username and password"""
        cursor = db.cursor()
        cursor.execute("""
            SELECT id, username, email, role, password_hash, created_at 
            FROM users WHERE username = ?
        """, (username,))
        
        row = cursor.fetchone()
        if row and check_password_hash(row[4], password):
            return User(row[0], row[1], row[2], row[3], row[5])
        return None
    
    @staticmethod
    def create(username, email, password, role='user', db=None):
        """Create new user"""
        password_hash = generate_password_hash(password)
        cursor = db.cursor()
        
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (username, email, password_hash, role, datetime.now()))
        
        db.commit()
        return User.get_by_username(username, db)


# ================= PERMISSION DECORATORS =================

def permission_required(permission):
    """Decorator to check if user has specific permission"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.has_permission(permission):
                return {"error": "Permission denied"}, 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            return {"error": "Admin access required"}, 403
        return f(*args, **kwargs)
    return decorated_function


def document_access_required(f):
    """Decorator to check document access"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        # Get document path from request
        doc_path = kwargs.get('doc_path') or request.args.get('filepath')
        
        if doc_path:
            from database import get_db
            db = get_db()
            if not current_user.can_access_document(doc_path, db):
                return {"error": "Access denied to this document"}, 403
        
        return f(*args, **kwargs)
    return decorated_function


# ================= LOGIN MANAGER SETUP =================

def init_login_manager(app):
    """Initialize Flask-Login"""
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        from database import get_db
        db = get_db()
        return User.get(user_id, db)
    
    return login_manager


# ================= HELPER FUNCTIONS =================

def grant_document_access(user_id, document_path, granted_by, db):
    """Grant user access to a specific document"""
    cursor = db.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO document_access 
        (user_id, document_path, granted_by, granted_at)
        VALUES (?, ?, ?, ?)
    """, (user_id, document_path, granted_by, datetime.now()))
    db.commit()


def revoke_document_access(user_id, document_path, db):
    """Revoke user access to a document"""
    cursor = db.cursor()
    cursor.execute("""
        DELETE FROM document_access 
        WHERE user_id = ? AND document_path = ?
    """, (user_id, document_path))
    db.commit()


def get_user_documents(user_id, db):
    """Get all documents accessible to a user"""
    cursor = db.cursor()
    
    # Get user info
    user = User.get(user_id, db)
    if not user:
        return []
    
    # Admins see everything
    if user.role == 'admin':
        cursor.execute("SELECT DISTINCT document_path FROM documents ORDER BY uploaded_at DESC")
        return [row[0] for row in cursor.fetchall()]
    
    # Regular users see their own documents + explicitly granted
    cursor.execute("""
        SELECT DISTINCT d.document_path 
        FROM documents d
        LEFT JOIN document_access da ON d.document_path = da.document_path
        WHERE d.uploaded_by = ? OR da.user_id = ?
        ORDER BY d.uploaded_at DESC
    """, (user_id, user_id))
    
    return [row[0] for row in cursor.fetchall()]


def log_access(user_id, action, resource, db):
    """Log user access for audit trail"""
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO access_log (user_id, action, resource, timestamp, ip_address)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, action, resource, datetime.now(), request.remote_addr if 'request' in globals() else None))
    db.commit()


def get_user_stats(user_id, db):
    """Get statistics for a user"""
    cursor = db.cursor()
    
    stats = {}
    
    # Document count
    cursor.execute("""
        SELECT COUNT(*) FROM documents WHERE uploaded_by = ?
    """, (user_id,))
    stats['documents'] = cursor.fetchone()[0]
    
    # Query count
    cursor.execute("""
        SELECT COUNT(*) FROM queries WHERE user_id = ?
    """, (user_id,))
    stats['queries'] = cursor.fetchone()[0]
    
    # Function executions
    cursor.execute("""
        SELECT COUNT(*) FROM function_executions WHERE user_id = ?
    """, (user_id,))
    stats['function_calls'] = cursor.fetchone()[0]
    
    # Last activity
    cursor.execute("""
        SELECT MAX(timestamp) FROM access_log WHERE user_id = ?
    """, (user_id,))
    stats['last_activity'] = cursor.fetchone()[0]
    
    return stats


def create_default_admin(db):
    """Create default admin user if none exists"""
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    
    if cursor.fetchone()[0] == 0:
        # Create default admin
        admin = User.create(
            username='admin',
            email='admin@example.com',
            password='admin123',  # CHANGE THIS!
            role='admin',
            db=db
        )
        print("⚠️  Default admin created: username=admin, password=admin123")
        print("⚠️  PLEASE CHANGE THE PASSWORD IMMEDIATELY!")
        return admin
    
    return None
