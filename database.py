"""
Database System for Metadata Storage
Add this as database.py in your project root
"""

import sqlite3
from datetime import datetime
from flask import g
import os
import json

DATABASE = 'rag_system.db'

# ================= DATABASE CONNECTION =================

def get_db():
    """Get database connection (Flask g object)"""
    if 'db' not in g:
        g.db = sqlite3.connect(
            DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Initialize database with schema"""
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    """)
    
    # Documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_path TEXT UNIQUE NOT NULL,
            filename TEXT NOT NULL,
            folder TEXT,
            file_type TEXT,
            file_size INTEGER,
            uploaded_by INTEGER NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_modified TIMESTAMP,
            is_indexed INTEGER DEFAULT 0,
            chunk_count INTEGER DEFAULT 0,
            metadata TEXT,
            FOREIGN KEY (uploaded_by) REFERENCES users(id)
        )
    """)
    
    # Document access control
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_access (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            document_path TEXT NOT NULL,
            granted_by INTEGER,
            granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, document_path),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (granted_by) REFERENCES users(id)
        )
    """)
    
    # Queries/searches table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            query_text TEXT NOT NULL,
            strategy TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            response_time REAL,
            chunks_retrieved INTEGER,
            llm_tokens INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Function executions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS function_executions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            function_name TEXT NOT NULL,
            parameters TEXT,
            result TEXT,
            status TEXT,
            execution_time REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Access log (audit trail)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS access_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            resource TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Index metadata
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS index_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            index_version TEXT,
            total_chunks INTEGER,
            total_documents INTEGER,
            embedding_model TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_rebuild TIMESTAMP
        )
    """)
    
    # User sessions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            ip_address TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Create indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_user ON documents(uploaded_by)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_path ON documents(document_path)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_queries_user ON queries(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_queries_timestamp ON queries(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_access_user ON document_access(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_access_log_user ON access_log(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_access_log_timestamp ON access_log(timestamp)")
    
    db.commit()
    db.close()
    
    print("✅ Database initialized successfully")


# ================= DOCUMENT OPERATIONS =================

def add_document(filepath, filename, folder, uploaded_by, db):
    """Add document to database"""
    cursor = db.cursor()
    
    file_type = filename.split('.')[-1].lower()
    file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
    
    cursor.execute("""
        INSERT OR REPLACE INTO documents 
        (document_path, filename, folder, file_type, file_size, uploaded_by, uploaded_at, last_modified)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (filepath, filename, folder, file_type, file_size, uploaded_by, 
          datetime.now(), datetime.now()))
    
    db.commit()
    return cursor.lastrowid


def update_document_index_status(document_path, is_indexed, chunk_count, db):
    """Update document indexing status"""
    cursor = db.cursor()
    cursor.execute("""
        UPDATE documents 
        SET is_indexed = ?, chunk_count = ?, last_modified = ?
        WHERE document_path = ?
    """, (is_indexed, chunk_count, datetime.now(), document_path))
    db.commit()


def get_document_info(document_path, db):
    """Get document information"""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM documents WHERE document_path = ?", (document_path,))
    return cursor.fetchone()


def delete_document(document_path, db):
    """Delete document from database"""
    cursor = db.cursor()
    cursor.execute("DELETE FROM documents WHERE document_path = ?", (document_path,))
    cursor.execute("DELETE FROM document_access WHERE document_path = ?", (document_path,))
    db.commit()


def get_user_documents_stats(user_id, db):
    """Get user's document statistics"""
    cursor = db.cursor()
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(file_size) as total_size,
            SUM(chunk_count) as total_chunks,
            COUNT(CASE WHEN is_indexed = 1 THEN 1 END) as indexed
        FROM documents
        WHERE uploaded_by = ?
    """, (user_id,))
    return cursor.fetchone()


# ================= QUERY OPERATIONS =================

def log_query(user_id, query_text, strategy, response_time, chunks_retrieved, db):
    """Log a search query"""
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO queries 
        (user_id, query_text, strategy, timestamp, response_time, chunks_retrieved)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, query_text, strategy, datetime.now(), response_time, chunks_retrieved))
    db.commit()
    return cursor.lastrowid


def get_user_queries(user_id, limit=10, db=None):
    """Get user's recent queries"""
    cursor = db.cursor()
    cursor.execute("""
        SELECT query_text, timestamp, strategy, response_time
        FROM queries
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (user_id, limit))
    return cursor.fetchall()


def get_popular_queries(limit=10, db=None):
    """Get most popular queries"""
    cursor = db.cursor()
    cursor.execute("""
        SELECT query_text, COUNT(*) as count
        FROM queries
        GROUP BY LOWER(query_text)
        ORDER BY count DESC
        LIMIT ?
    """, (limit,))
    return cursor.fetchall()


# ================= FUNCTION EXECUTION LOGGING =================

def log_function_execution(user_id, function_name, parameters, result, status, execution_time, db):
    """Log function execution"""
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO function_executions
        (user_id, function_name, parameters, result, status, execution_time, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, function_name, json.dumps(parameters), str(result)[:1000], 
          status, execution_time, datetime.now()))
    db.commit()


def get_function_stats(db):
    """Get function execution statistics"""
    cursor = db.cursor()
    cursor.execute("""
        SELECT 
            function_name,
            COUNT(*) as call_count,
            AVG(execution_time) as avg_time,
            SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
            SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_count
        FROM function_executions
        GROUP BY function_name
        ORDER BY call_count DESC
    """)
    return cursor.fetchall()


# ================= INDEX METADATA =================

def save_index_metadata(total_chunks, total_documents, embedding_model, db):
    """Save index metadata"""
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO index_metadata 
        (index_version, total_chunks, total_documents, embedding_model, created_at, last_rebuild)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('1.0', total_chunks, total_documents, embedding_model, 
          datetime.now(), datetime.now()))
    db.commit()


def get_latest_index_metadata(db):
    """Get latest index metadata"""
    cursor = db.cursor()
    cursor.execute("""
        SELECT * FROM index_metadata 
        ORDER BY created_at DESC 
        LIMIT 1
    """)
    return cursor.fetchone()


# ================= ANALYTICS =================

def get_system_stats(db):
    """Get overall system statistics"""
    cursor = db.cursor()
    
    stats = {}
    
    # Total users
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
    stats['total_users'] = cursor.fetchone()[0]
    
    # Total documents
    cursor.execute("SELECT COUNT(*) FROM documents")
    stats['total_documents'] = cursor.fetchone()[0]
    
    # Total queries
    cursor.execute("SELECT COUNT(*) FROM queries")
    stats['total_queries'] = cursor.fetchone()[0]
    
    # Total function calls
    cursor.execute("SELECT COUNT(*) FROM function_executions")
    stats['total_function_calls'] = cursor.fetchone()[0]
    
    # Active users (logged in last 7 days)
    cursor.execute("""
        SELECT COUNT(DISTINCT user_id) 
        FROM access_log 
        WHERE timestamp > datetime('now', '-7 days')
    """)
    stats['active_users_week'] = cursor.fetchone()[0]
    
    # Average query response time
    cursor.execute("SELECT AVG(response_time) FROM queries")
    stats['avg_response_time'] = cursor.fetchone()[0]
    
    return stats


def get_user_activity(user_id, days=7, db=None):
    """Get user activity for last N days"""
    cursor = db.cursor()
    cursor.execute("""
        SELECT 
            DATE(timestamp) as date,
            COUNT(*) as activity_count
        FROM access_log
        WHERE user_id = ? AND timestamp > datetime('now', '-' || ? || ' days')
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
    """, (user_id, days))
    return cursor.fetchall()


# ================= CLEANUP =================

def cleanup_old_sessions(db):
    """Remove expired sessions"""
    cursor = db.cursor()
    cursor.execute("DELETE FROM sessions WHERE expires_at < ?", (datetime.now(),))
    db.commit()


def cleanup_old_logs(days=90, db=None):
    """Remove old access logs"""
    cursor = db.cursor()
    cursor.execute("""
        DELETE FROM access_log 
        WHERE timestamp < datetime('now', '-' || ? || ' days')
    """, (days,))
    db.commit()


# ================= BACKUP =================

def backup_database(backup_path=None):
    """Backup database to file"""
    if backup_path is None:
        backup_path = f"backups/rag_system_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    
    source = sqlite3.connect(DATABASE)
    dest = sqlite3.connect(backup_path)
    source.backup(dest)
    dest.close()
    source.close()
    
    print(f"✅ Database backed up to: {backup_path}")
    return backup_path
