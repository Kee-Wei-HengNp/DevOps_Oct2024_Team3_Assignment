import sqlite3

# Connect to SQLite database (creates file if it doesn't exist)
conn = sqlite3.connect('users.db')

# Create a cursor object
cursor = conn.cursor()

# Create a table for users
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
''')

# Insert some test users (admin and student)
cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', ('admin_user', 'adminpass', 'admin'))
cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', ('student_user', 'studentpass', 'student'))

# Commit and close the connection
conn.commit()
conn.close()

print("Database setup complete!")