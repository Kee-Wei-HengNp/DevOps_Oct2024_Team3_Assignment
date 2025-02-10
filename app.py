import sqlite3
import random
from flask import Flask, render_template, request, jsonify,session, redirect, url_for

app = Flask(__name__)

# ✅ Add session configurations here
app.secret_key = 'supersecretkey'  # Required for session management
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'  # Store session in a file (persistent across requests)


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

    print(f"Login Attempt: username={username}, password={password}")  # ✅ Debug login attempt

    if not username or not password:
        return jsonify({"success": False, "message": "Username or password is missing!"}), 400

    user = get_user_from_db(username)
    if user and user[1] == password:  # Check if password matches
        role = user[2]  # Get the role (admin or student)

         # ✅ Store session data
        session["username"] = username
        session["role"] = role
        print(f"Session After Login: {session}")  # ✅ Debug session after login

        redirect_url = "/admin" if role == "admin" else "/student"
        return jsonify({"success": True, "redirect_url": redirect_url})
    else:
        return jsonify({"success": False, "message": "Invalid username or password"}), 401


@app.route('/admin')
def admin_page():
    print(f"Session Data: {session}")  # ✅ Debugging session
    if "username" not in session or session.get("role") != "admin":
        return redirect(url_for("home"))  # Redirect unauthorized users
    return "Welcome to Admin Page"  


@app.route('/student')
def student_page():
    print(f"Session Data: {session}")  # ✅ Debugging session
    if "username" not in session or session.get("role") != "student":
        return redirect(url_for("home"))  # Redirect unauthorized users

    user_data = {
        "username": session["username"],
        "points": random.randint(0, 9999)
    }
    return render_template('student.html', username=user_data["username"], points=user_data["points"])


@app.route('/redeemable-items')
def redeemable_items():
    return render_template('redeemable_items.html')


@app.route('/redeemed-items')
def redeemed_items():
    return render_template('redeemed_items.html')


@app.route('/recover-password')
def recover_password():
    return render_template('recover_password.html')

@app.route('/logout')
def logout():
    session.clear()  # ✅ Clears all session data (logs user out)
    return redirect(url_for('home'))  # ✅ Redirect to login page

if __name__ == '__main__':
    app.run(debug=True)
