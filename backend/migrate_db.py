"""
Database Migration Script
Adds user_id column to existing chat_sessions table
Run this ONCE after pulling the authentication changes
"""

import sqlite3

DB_PATH = "fir.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if user_id column already exists
        cursor.execute("PRAGMA table_info(chat_sessions)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'user_id' not in columns:
            print("Adding user_id column to chat_sessions table...")
            cursor.execute("ALTER TABLE chat_sessions ADD COLUMN user_id INTEGER")
            conn.commit()
            print("✅ Migration completed successfully!")
        else:
            print("⚠️ user_id column already exists. No migration needed.")
    
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting database migration...")
    migrate()
