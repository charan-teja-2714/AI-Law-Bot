import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'fir.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if email column exists
cursor.execute("PRAGMA table_info(users)")
columns = [col[1] for col in cursor.fetchall()]

if 'email' not in columns:
    print("Adding email column to users table...")
    cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    conn.commit()
    print("Email column added successfully!")
else:
    print("Email column already exists.")

conn.close()
print("Database migration complete.")
