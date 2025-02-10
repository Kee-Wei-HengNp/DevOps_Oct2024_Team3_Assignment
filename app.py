import sqlite3
import random
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import csv  # ✅ Required for CSV handling


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

    # ✅ Prevent unauthorized access
    if "username" not in session or session.get("role") != "admin":
        return redirect(url_for("home"))  # Redirect unauthorized users to home

    # ✅ Fetch student list from the database
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE role = 'student'")
    students = cursor.fetchall()  # Fetch all students as a list of tuples
    conn.close()

    # ✅ Render admin.html with student data
    return render_template("admin.html", username=session["username"], students=students)

# ✅ Create New Student
@app.route('/add_student', methods=['POST'])
def add_student():
    if "username" not in session or session.get("role") != "admin":
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required!"})

    conn = db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'student')", (username, password))
        conn.commit()
        return jsonify({"success": True, "message": "Student added successfully!"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Username already exists!"})
    finally:
        conn.close()


# ✅ Edit a student username
@app.route('/update-student', methods=['POST'])
def update_student():
    data = request.json
    student_id = data.get("id")
    new_username = data.get("username")
    new_password = data.get("password")

    if not student_id or not new_username or not new_password:
        return jsonify({"success": False, "message": "Missing data: ID, username, and password are required."}), 400

    conn = db_connection()
    cursor = conn.cursor()

    try:
        # ✅ Ensure username is unique (Optional)
        cursor.execute("SELECT id FROM users WHERE username = ? AND id != ?", (new_username, student_id))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "Username already exists!"})

        cursor.execute("UPDATE users SET username = ?, password = ? WHERE id = ?", (new_username, new_password, student_id))
        conn.commit()

        return jsonify({"success": True, "message": "Student updated successfully!"})  # ✅ Always return message
    except sqlite3.Error as e:
        return jsonify({"success": False, "message": str(e)})
    finally:
        conn.close()



# ✅ Delete a student
@app.route('/delete-student', methods=['POST'])
def delete_student():
    data = request.json
    student_id = data.get("id")

    if not student_id:
        return jsonify({"success": False, "message": "Invalid student ID"}), 400

    conn = db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM users WHERE id = ?", (student_id,))
        conn.commit()
        
        return jsonify({"success": True, "message": "Student deleted successfully!"})  # ✅ Always return message
    except sqlite3.Error as e:
        return jsonify({"success": False, "message": str(e)})
    finally:
        conn.close()
        
# ✅ Search Student
@app.route('/search_student', methods=['GET'])
def search_student():
    if "username" not in session or session.get("role") != "admin":
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    query = request.args.get("query", "").strip()
    if not query:
        return jsonify({"success": False, "message": "Search query is required!"})

    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE username LIKE ? OR id LIKE ?", (f"%{query}%", f"%{query}%"))
    students = cursor.fetchall()
    conn.close()

    return jsonify({"success": True, "students": [dict(row) for row in students]})


# ✅ Bulk Upload Students via CSV
@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if "username" not in session or session.get("role") != "admin":
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    file = request.files.get("file")
    if not file:
        return jsonify({"success": False, "message": "No file uploaded!"})

    conn = db_connection()
    cursor = conn.cursor()

    csv_reader = csv.reader(file.stream.read().decode("utf-8").splitlines())
    next(csv_reader)  # Skip header row

    for row in csv_reader:
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'student')", (row[0], row[1]))
        except sqlite3.IntegrityError:
            continue  # Skip duplicate usernames

    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "CSV data uploaded successfully!"})

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
    return render_template('recovery_page.html')

@app.route('/logout')
def logout():
    session.clear()  # ✅ Clears all session data (logs user out)
    return redirect(url_for('home'))  # ✅ Redirect to login page



if __name__ == '__main__':
    app.run(debug=True)
