import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Helper function to connect to the database
def db_connection():
    conn = sqlite3.connect('users.db')
    return conn

# Function to get user from database
def get_user_from_db(username):
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT username, password, role FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()

    conn.close()
    return user

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username or password is missing!"}), 400

    user = get_user_from_db(username)
    if user and user[1] == password:  # Check if password matches
        role = user[2]  # Get the role (admin or student)
        redirect_url = "/admin" if role == "admin" else "/student"
        return jsonify({"success": True, "redirect_url": redirect_url})
    else:
        return jsonify({"success": False, "message": "Invalid username or password"}), 401

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@app.route('/student')
def student_page():
    return render_template('student.html')

@app.route('/recover-password')
def recover_password():
    return render_template('recover_password.html')

if __name__ == '__main__':
    app.run(debug=True)
