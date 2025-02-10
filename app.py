import sqlite3
import random
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

    cursor.execute(
        'SELECT username, password, role FROM users WHERE username = ?', (username,))
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
    # Dummy user data (will be replaced with real session-based data later)
    user_data = {
        "username": "test_student",
        "points": random.randint(0, 9999)  # Random value for now
    }
    return render_template('student.html', username=user_data["username"], points=user_data["points"])


@app.route('/redeemable-items')
def redeemable_items():
    return render_template('redeemable_items.html')

@app.route('/create-account')
def create_account():
    return render_template('create_account.html')

@app.route('/modify-account')
def modify_account():
    return render_template('modify_account.html')

@app.route('/delete-account')
def delete_account():
    return render_template('delete_account.html')

@app.route('/redeemed-items')
def redeemed_items():
    return render_template('redeemed_items.html')


@app.route('/recover-password')
def recover_password():
    return render_template('recovery_page.html')


if __name__ == '__main__':
    app.run(debug=True)
