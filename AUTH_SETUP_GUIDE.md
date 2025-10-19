# Authentication & Database Setup Guide

## 📦 What You're Adding

1. **User Authentication** - Login/logout, user roles
2. **Document Access Control** - Users only see their own documents
3. **Database** - SQLite for metadata storage
4. **Audit Logging** - Track all user actions

## 🚀 Installation Steps

### Step 1: Install Dependencies

```bash
pip install Flask-Login
```

### Step 2: Add New Files

Create these new files in your project root:

1. **`auth.py`** - Copy from artifact above
2. **`database.py`** - Copy from artifact above

Create template files:

3. **`templates/login.html`** - Copy from artifact
4. **`templates/register.html`** - Copy from artifact

### Step 3: Modify app.py

Add the integration code from `app_integration.py` artifact:

**At the top (imports):**
```python
from flask_login import login_user, logout_user, login_required, current_user
from auth import User, init_login_manager, permission_required, document_access_required, create_default_admin
from database import *
import time
```

**After `app = Flask(__name__)`:**
```python
# Initialize database
init_db()

# Initialize authentication  
login_manager = init_login_manager(app)

# Register database teardown
app.teardown_appcontext(close_db)

# Create default admin
with app.app_context():
    db = get_db()
    create_default_admin(db)
```

**Add new routes:**
- `/login`
- `/logout`
- `/register`
- `/profile`
- `/admin`

**Modify existing routes:**
- Add `@login_required` decorator to `/`, `/ask`, `/doc`
- Filter documents by user access

(See full code in `app_integration.py` artifact)

### Step 4: Test

```bash
# Start app
python app.py

# You should see:
# ⚠️  Default admin created: username=admin, password=admin123
# ⚠️  PLEASE CHANGE THE PASSWORD IMMEDIATELY!

# Open browser
http://localhost:5000

# You'll be redirected to login page
# Login with: admin / admin123
```

## 🎯 How It Works

### User Roles

| Role | Permissions |
|------|-------------|
| **admin** | Read, write, delete, manage users, view all documents |
| **user** | Read, write (own documents only) |
| **viewer** | Read only |

### Document Access

**Users see only:**
1. Documents they uploaded
2. Documents explicitly shared with them
3. Admins see everything

**Folder structure:**
```
uploaded_docs/
├── alice/
│   ├── reports/
│   │   └── report1.pdf
│   └── data/
│       └── sales.xlsx
└── bob/
    └── projects/
        └── analysis.txt
```

### Database Tables

1. **users** - User accounts
2. **documents** - Document metadata
3. **document_access** - Access control
4. **queries** - Search history
5. **function_executions** - Function call logs
6. **access_log** - Audit trail
7. **index_metadata** - FAISS index info
8. **sessions** - User sessions

## 🔒 Security Features

✅ **Password hashing** - Using Werkzeug SHA256
✅ **Session management** - Flask-Login
✅ **Access control** - Role-based permissions
✅ **Audit logging** - All actions tracked
✅ **Document isolation** - Users can't access others' files
✅ **SQL injection prevention** - Parameterized queries

## 📊 What Gets Logged

**Access Log:**
- User logins/logouts
- Document uploads
- Document downloads
- Queries
- Function executions
- Admin actions

**Query:**
```python
# View logs
sqlite3 rag_system.db
SELECT * FROM access_log ORDER BY timestamp DESC LIMIT 10;
```

## 🛠️ Common Tasks

### Create New User (CLI)

```python
python
>>> from database import get_db, init_db
>>> from auth import User
>>> import sqlite3
>>> 
>>> db = sqlite3.connect('rag_system.db')
>>> user = User.create('john', 'john@example.com', 'password123', 'user', db)
>>> print(f"Created user: {user.username}")
```

### Change User Role

```python
sqlite3 rag_system.db
UPDATE users SET role = 'admin' WHERE username = 'john';
```

### Grant Document Access

```python
# In Python console
from database import get_db
from auth import grant_document_access

db = get_db()
grant_document_access(
    user_id=2,
    document_path='uploaded_docs/alice/reports/report1.pdf',
    granted_by=1,  # admin
    db=db
)
```

### View User Statistics

```python
from database import get_db
from auth import get_user_stats

db = get_db()
stats = get_user_stats(user_id=2, db=db)
print(stats)
```

### Backup Database

```python
from database import backup_database

backup_path = backup_database()
print(f"Backup saved to: {backup_path}")
```

## 🎨 Customization

### Change Password Requirements

In `templates/register.html`:
```html
<input type="password" minlength="8" required pattern="(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}">
<!-- Requires: 8+ chars, 1 uppercase, 1 lowercase, 1 number -->
```

### Add More User Roles

In `auth.py`:
```python
permissions = {
    'admin': ['read', 'write', 'delete', 'manage_users', 'view_all'],
    'user': ['read', 'write'],
    'viewer': ['read'],
    'editor': ['read', 'write', 'share'],  # Add this
}
```

### Custom Access Rules

In `User.can_access_document()`:
```python
# Allow access to documents in 'public' folder
if 'public/' in document_path:
    return True
```

## 🐛 Troubleshooting

**Issue: "Table users doesn't exist"**
```bash
# Reinitialize database
python
>>> from database import init_db
>>> init_db()
```

**Issue: "Cannot login with admin"**
```bash
# Check if admin exists
sqlite3 rag_system.db
SELECT * FROM users WHERE username = 'admin';

# If not, create manually:
python
>>> from database import get_db
>>> from auth import create_default_admin
>>> import sqlite3
>>> db = sqlite3.connect('rag_system.db')
>>> create_default_admin(db)
```

**Issue: "Access denied to document"**
- Check user role: `SELECT role FROM users WHERE username = 'yourname';`
- Check document owner: `SELECT uploaded_by FROM documents WHERE document_path = '...';`
- Grant access if needed (see Common Tasks above)

**Issue: "Database locked"**
```bash
# Close all connections
pkill -9 python
rm rag_system.db-journal  # If exists
```

**Issue: "User folder not created"**
- Folders created automatically on first upload
- Or manually: `mkdir -p uploaded_docs/username/general`

## 🔥 Quick Test Checklist

After setup, test these:

```bash
# 1. Database created
ls -la rag_system.db

# 2. Login page accessible
curl http://localhost:5000
# Should redirect to /login

# 3. Admin login works
# Browser: http://localhost:5000/login
# Username: admin
# Password: admin123

# 4. Upload works (user-isolated)
# Upload a file - check it goes to uploaded_docs/admin/

# 5. Query logs to database
sqlite3 rag_system.db
SELECT COUNT(*) FROM queries;

# 6. Function execution logs
SELECT COUNT(*) FROM function_executions;

# 7. Access log works
SELECT action, resource FROM access_log ORDER BY timestamp DESC LIMIT 5;
```

## 📈 Monitoring Queries

### Most Active Users
```sql
sqlite3 rag_system.db
SELECT u.username, COUNT(*) as query_count
FROM queries q
JOIN users u ON q.user_id = u.id
GROUP BY u.username
ORDER BY query_count DESC;
```

### Most Used Functions
```sql
SELECT function_name, COUNT(*) as calls
FROM function_executions
GROUP BY function_name
ORDER BY calls DESC
LIMIT 10;
```

### Failed Function Calls
```sql
SELECT function_name, COUNT(*) as failures
FROM function_executions
WHERE status = 'error'
GROUP BY function_name
ORDER BY failures DESC;
```

### Average Query Time
```sql
SELECT AVG(response_time) as avg_seconds
FROM queries
WHERE timestamp > datetime('now', '-7 days');
```

### User Activity (Last 24h)
```sql
SELECT u.username, COUNT(*) as actions
FROM access_log al
JOIN users u ON al.user_id = u.id
WHERE al.timestamp > datetime('now', '-1 day')
GROUP BY u.username;
```

## 🔐 Production Security Checklist

Before deploying:

- [ ] Change default admin password
- [ ] Set strong `app.secret_key` (not 'super-secret-key')
- [ ] Enable HTTPS (use Flask-Talisman)
- [ ] Add rate limiting (Flask-Limiter)
- [ ] Set secure session cookies
- [ ] Regular database backups
- [ ] Monitor access logs
- [ ] Update dependencies regularly
- [ ] Use environment variables for secrets

### Enable HTTPS

```bash
pip install Flask-Talisman
```

```python
# In app.py, after app = Flask(__name__)
from flask_talisman import Talisman
Talisman(app, force_https=True)
```

### Add Rate Limiting

```bash
pip install Flask-Limiter
```

```python
# In app.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route("/ask")
@limiter.limit("10 per minute")
@login_required
def ask():
    pass
```

### Secure Session Configuration

```python
# In app.py
app.config.update(
    SESSION_COOKIE_SECURE=True,  # HTTPS only
    SESSION_COOKIE_HTTPONLY=True,  # No JavaScript access
    SESSION_COOKIE_SAMESITE='Lax',  # CSRF protection
    PERMANENT_SESSION_LIFETIME=timedelta(hours=24)
)
```

### Use Environment Variables

```bash
# Create .env file
SECRET_KEY=your-very-long-random-secret-key-here
DATABASE_URL=sqlite:///rag_system.db
```

```python
# In app.py
from dotenv import load_dotenv
import os

load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')
```

## 📊 Database Maintenance

### Regular Backups

```python
# Add to app.py
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=backup_database,
    trigger="interval",
    hours=24,
    id='daily_backup'
)
scheduler.start()
```

### Cleanup Old Logs

```python
# Monthly cleanup
from database import cleanup_old_logs

# Keep logs for 90 days
cleanup_old_logs(days=90, db=get_db())
```

### Vacuum Database (Optimize)

```bash
sqlite3 rag_system.db
VACUUM;
```

## 🎯 User Management Examples

### List All Users

```bash
sqlite3 rag_system.db
SELECT id, username, email, role, created_at, last_login 
FROM users 
ORDER BY created_at DESC;
```

### Deactivate User

```sql
UPDATE users SET is_active = 0 WHERE username = 'john';
```

### Reactivate User

```sql
UPDATE users SET is_active = 1 WHERE username = 'john';
```

### Delete User (with cleanup)

```python
# Python script
import sqlite3

db = sqlite3.connect('rag_system.db')
cursor = db.cursor()

user_id = 2  # User to delete

# Delete in order (foreign keys)
cursor.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
cursor.execute("DELETE FROM access_log WHERE user_id = ?", (user_id,))
cursor.execute("DELETE FROM function_executions WHERE user_id = ?", (user_id,))
cursor.execute("DELETE FROM queries WHERE user_id = ?", (user_id,))
cursor.execute("DELETE FROM document_access WHERE user_id = ?", (user_id,))
cursor.execute("DELETE FROM documents WHERE uploaded_by = ?", (user_id,))
cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))

db.commit()
print(f"User {user_id} deleted")
```

## 🌟 Advanced Features

### Email Notifications

```python
# When user registers
from flask_mail import Mail, Message

mail = Mail(app)

@app.route("/register", methods=["POST"])
def register():
    # ... create user ...
    
    msg = Message(
        "Welcome to RAG System",
        recipients=[email],
        body=f"Hello {username}, your account has been created!"
    )
    mail.send(msg)
```

### Password Reset

```python
# Generate reset token
import secrets

token = secrets.token_urlsafe(32)

# Store in database with expiry
cursor.execute("""
    INSERT INTO password_resets (user_id, token, expires_at)
    VALUES (?, ?, datetime('now', '+1 hour'))
""", (user_id, token))
```

### Two-Factor Authentication

```bash
pip install pyotp qrcode
```

```python
import pyotp

# Generate secret for user
secret = pyotp.random_base32()

# Store in users table
# Add column: totp_secret TEXT

# Verify code
totp = pyotp.TOTP(secret)
is_valid = totp.verify(user_code)
```

## 📚 API Examples

### Get User Info (Authenticated)

```bash
curl -H "Cookie: session=..." http://localhost:5000/api/user/stats
```

### Upload Document (Authenticated)

```bash
curl -X POST \
  -H "Cookie: session=..." \
  -F "file=@document.pdf" \
  -F "folder=reports" \
  http://localhost:5000/
```

### Query (Authenticated)

```bash
curl -X POST \
  -H "Cookie: session=..." \
  -d "question=What is in the report?" \
  http://localhost:5000/ask
```

## ✅ Final Checklist

Setup complete when:

- [ ] Database `rag_system.db` exists
- [ ] Can login with admin/admin123
- [ ] Can register new user
- [ ] Upload creates user-specific folders
- [ ] Users only see their own documents
- [ ] Queries logged to database
- [ ] Function calls logged
- [ ] Access log populated
- [ ] Admin can see all documents
- [ ] Regular users isolated

## 🎉 Summary

You've now added:

✅ **Authentication** - Secure login/logout system
✅ **User Management** - Roles and permissions
✅ **Document Isolation** - Users can't access others' files
✅ **Database** - SQLite for metadata
✅ **Audit Logging** - Complete activity tracking
✅ **Access Control** - Fine-grained permissions
✅ **Statistics** - User and system analytics

Your RAG system is now **production-ready** with proper security! 🚀

**Next Steps:**
1. Change admin password
2. Create test users
3. Upload documents
4. Test access control
5. Monitor logs
6. Set up backups
7. Enable HTTPS for production
