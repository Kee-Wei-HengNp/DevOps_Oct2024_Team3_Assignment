import sqlite3
import csv
import os

# ✅ Database file name
DB_NAME = "users.db"


import sqlite3

def setup_database():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # ✅ Ensure the `users` table exists
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        points INTEGER DEFAULT 0
    )''')

    # ✅ Ensure the `redeemed_items` table exists
    cursor.execute('''CREATE TABLE IF NOT EXISTS redeemed_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        item_name TEXT NOT NULL,
        FOREIGN KEY(username) REFERENCES users(username)
    )''')

    # ✅ Ensure the `redeemable_items` table exists
    cursor.execute('''CREATE TABLE IF NOT EXISTS redeemable_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        cost INTEGER NOT NULL
    )''')

    # ✅ Insert sample redeemable items if none exist
    cursor.execute("INSERT OR IGNORE INTO redeemable_items (name, cost) VALUES ('AAA', 200)")
    cursor.execute("INSERT OR IGNORE INTO redeemable_items (name, cost) VALUES ('BBB', 300)")
    cursor.execute("INSERT OR IGNORE INTO redeemable_items (name, cost) VALUES ('CCC', 400)")

    conn.commit()
    conn.close()

setup_database()



# ✅ Function to connect to the database
def db_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn

# ✅ Function to initialize the database and create tables
def initialize_database():
    conn = db_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            points INTEGER DEFAULT 0
        )
    ''')
    

    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

# ✅ Function to insert a new user
def insert_user(username, password, role):
    conn = db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                       (username, password, role))
        conn.commit()
        print(f"✅ User {username} added successfully!")
    except sqlite3.IntegrityError:
        print(f"❌ User {username} already exists!")
    
    conn.close()

# ✅ Function to fetch all users
def get_all_users():
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    conn.close()
    return users

# ✅ Function to update user password
def update_user_password(username, new_password):
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
    conn.commit()
    conn.close()

    print(f"✅ Password updated for {username}!")

# ✅ Function to delete a user
def delete_user(username):
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()

    print(f"✅ User {username} deleted successfully!")

# ✅ Function to bulk insert users from CSV
def bulk_insert_from_csv(csv_file):
    conn = db_connection()
    cursor = conn.cursor()

    try:
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row

            for row in reader:
                username, password, role = row
                cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                               (username, password, role))

        conn.commit()
        print(f"✅ Bulk data from {csv_file} inserted successfully!")
    except Exception as e:
        print(f"❌ Error inserting from CSV: {e}")

    conn.close()

# ✅ Function to print all users
def display_all_users():
    users = get_all_users()
    print("\n📌 Current Users in Database:")
    print("-" * 40)
    for user in users:
        print(f"ID: {user[0]}, Username: {user[1]}, Role: {user[3]}")
    print("-" * 40)

# ✅ Run the database setup when this script is executed
if __name__ == "__main__":
    initialize_database()  # ✅ Ensure DB is initialized
    insert_user("admin_user", "adminpass", "admin")  # ✅ Add default admin
    insert_user("student_user", "studentpass", "student")  # ✅ Add default student
    display_all_users()  # ✅ Show all users
