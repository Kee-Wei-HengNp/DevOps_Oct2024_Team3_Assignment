import sqlite3
import random
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import csv  # ✅ Required for CSV handling
import os

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

    # ✅ Fetch students including points
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, points FROM users WHERE role = 'student'")
    students = cursor.fetchall()
    conn.close()

    # ✅ Render the Admin Page with updated students list
    return render_template("admin.html", username=session["username"], students=students)



# ✅ Upload CSV File & Populate Database
@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file provided!"}), 400

    file = request.files['file']

    if not file.filename.endswith('.csv'):
        return jsonify({"success": False, "message": "Invalid file format. Only CSV allowed!"}), 400

    conn = db_connection()
    cursor = conn.cursor()

    try:
        file_path = os.path.join("uploads", file.filename)
        file.save(file_path)

        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header row

            for row in reader:
                if len(row) < 3:
                    continue  # Ignore incomplete rows
                
                username, password, points = row[0], row[1], row[2]
                cursor.execute("INSERT INTO users (username, password, role, points) VALUES (?, ?, ?, ?)",
                               (username, password, 'student', points))
        
        conn.commit()
        return jsonify({"success": True, "message": "Students uploaded successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
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
        # ✅ Check if the student exists before deleting
        cursor.execute("SELECT * FROM users WHERE id = ?", (student_id,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"success": False, "message": "Student does not exist"}), 400

        # ✅ If student exists, proceed with deletion
        # ✅ Check if the student exists before deleting
        cursor.execute("SELECT * FROM users WHERE id = ?", (student_id,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"success": False, "message": "Student does not exist"}), 400

        # ✅ If student exists, proceed with deletion
        # ✅ Check if the student exists before deleting
        cursor.execute("SELECT * FROM users WHERE id = ?", (student_id,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"success": False, "message": "Student does not exist"}), 400

        # ✅ If student exists, proceed with deletion
        cursor.execute("DELETE FROM users WHERE id = ?", (student_id,))
        conn.commit()

        return jsonify({"success": True, "message": "Student deleted successfully!"})
    

        return jsonify({"success": True, "message": "Student deleted successfully!"})
    

        return jsonify({"success": True, "message": "Student deleted successfully!"})
    
    except sqlite3.Error as e:
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500
    
    
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500
    
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500
    
    finally:
        conn.close()



        
# ✅ Search Student
@app.route('/search_students', methods=['POST'])
def search_students():
    data = request.json
    search_query = data.get('query', '')

    conn = db_connection()
    cursor = conn.cursor()

    # ✅ Search by ID or Username (case-insensitive)
    cursor.execute("SELECT id, username, points FROM users WHERE role='student' AND (id LIKE ? OR username LIKE ?)", 
                   ('%' + search_query + '%', '%' + search_query + '%'))

    students = cursor.fetchall()
    conn.close()

    return jsonify({"students": students})



@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    points = data.get('points')  # ✅ Get points

    if not username or not password or points is None:
        return jsonify({"success": False, "message": "All fields are required!"}), 400

    conn = db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, password, role, points) VALUES (?, ?, 'student', ?)", 
                       (username, password, points))  # ✅ Insert points
        conn.commit()
        return jsonify({"success": True, "message": "Student added successfully!"})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": "Failed to add student."}), 500
    finally:
        conn.close()

@app.route('/student')
def student_page():
    """Render the student dashboard."""
    """Render the student dashboard."""
    """Render the student dashboard."""
    if "username" not in session or session.get("role") != "student":
        return redirect(url_for("home"))  # Redirect unauthorized users to login

    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, points FROM users WHERE username=?", (session["username"],))
    user_data = cursor.fetchone()
    conn.close()

    if not user_data:
        return "Student record not found!", 404  # 🔹 Simplified error response

    return render_template('student.html', username=user_data[0], points=user_data[1])
   
   


    if not user_data:
        return "Student record not found!", 404  # 🔹 Simplified error response

    return render_template('student.html', username=user_data[0], points=user_data[1])
   


    if not user_data:
        return "Student record not found!", 404  # 🔹 Simplified error response

    return render_template('student.html', username=user_data[0], points=user_data[1])
   



# Dummy redeemable items
redeemable_items = [
    {"name": "AAA", "cost": 200},
    {"name": "BBB", "cost": 300},
    {"name": "CCC", "cost": 400}
]


@app.route('/redeemable-items')
def redeemable_items_page():
    """Display available redeemable items."""
    if "username" not in session or session.get("role") != "student":
        return redirect(url_for("home"))  # Redirect unauthorized users

    conn = db_connection()
    cursor = conn.cursor()

    # ✅ Fetch user points
    cursor.execute("SELECT points FROM users WHERE username=?", (session["username"],))
    user = cursor.fetchone()

    if not user:
        return "❌ Student record not found!", 404

    points = user[0]

    # ✅ Fetch redeemable items from database
    # ✅ Fetch redeemable items
    cursor.execute("SELECT name, cost FROM redeemable_items")
    items = cursor.fetchall()
    conn.close()

    return render_template('redeemable_items.html', points=points, items=items)


    if "username" not in session or session.get("role") != "student":
        return redirect(url_for("home"))

    conn = db_connection()
    cursor = conn.cursor()

    # ✅ Fetch user points
    cursor.execute("SELECT points FROM users WHERE username=?", (session["username"],))
    user = cursor.fetchone()
    
    if not user:
        return "Student record not found!", 404

    points = user[0]

    # ✅ Fetch redeemable items
    cursor.execute("SELECT name, cost FROM redeemable_items")
    items = cursor.fetchall()
    conn.close()

    return render_template('redeemable_items.html', points=points, items=items)


    if "username" not in session or session.get("role") != "student":
        return redirect(url_for("home"))

    conn = db_connection()
    cursor = conn.cursor()

    # ✅ Fetch user points
    cursor.execute("SELECT points FROM users WHERE username=?", (session["username"],))
    user = cursor.fetchone()
    
    if not user:
        return "Student record not found!", 404

    points = user[0]

    # ✅ Fetch redeemable items
    cursor.execute("SELECT name, cost FROM redeemable_items")
    items = cursor.fetchall()
    conn.close()

    return render_template('redeemable_items.html', points=points, items=items)

@app.route('/redeemed-items')
def redeemed_items_page():
    """Display all previously redeemed items."""
    if "username" not in session or session.get("role") != "student":
        return redirect(url_for("home"))  # Redirect unauthorized users

    conn = db_connection()
    cursor = conn.cursor()

    # ✅ Fetch redeemed items from the database instead of `students`
    cursor.execute("SELECT item_name FROM redeemed_items WHERE username=?", (session["username"],))
    redeemed_items = cursor.fetchall()
    conn.close()

    return render_template('redeemed_items.html', items=[item[0] for item in redeemed_items])

    if "username" not in session or session.get("role") != "student":
        return redirect(url_for("home"))  # Redirect unauthorized users

    conn = db_connection()
    cursor = conn.cursor()

    # ✅ Fetch redeemed items from the database instead of `students`
    cursor.execute("SELECT item_name FROM redeemed_items WHERE username=?", (session["username"],))
    redeemed_items = cursor.fetchall()
    conn.close()

    return render_template('redeemed_items.html', items=[item[0] for item in redeemed_items])

    if "username" not in session or session.get("role") != "student":
        return redirect(url_for("home"))  # Redirect unauthorized users

    conn = db_connection()
    cursor = conn.cursor()

    # ✅ Fetch redeemed items from the database instead of `students`
    cursor.execute("SELECT item_name FROM redeemed_items WHERE username=?", (session["username"],))
    redeemed_items = cursor.fetchall()
    conn.close()

    return render_template('redeemed_items.html', items=[item[0] for item in redeemed_items])



@app.route('/recover-password')
def recover_password():
    return render_template('recovery_page.html')

@app.route('/logout')
def logout():
    session.clear()  # ✅ Clears all session data (logs user out)
    return redirect(url_for('home'))  # ✅ Redirect to login page


@app.route('/redeem-item', methods=['POST'])
def redeem_item():
    """Handle item redemption."""
    if "username" not in session or session.get("role") != "student":
        return redirect(url_for("home"))

    data = request.json
    item_name = data.get("item")

    # ✅ Open database connection
    with db_connection() as conn:
        cursor = conn.cursor()

        # ✅ Fetch user points
        cursor.execute("SELECT points FROM users WHERE username=?", (session["username"],))
        user = cursor.fetchone()

        if not user:
            return jsonify({"success": False, "message": "Student record not found!"}), 404

        user_points = user[0]

        # ✅ Fetch item cost
        cursor.execute("SELECT cost FROM redeemable_items WHERE name=?", (item_name,))
        item = cursor.fetchone()

        if not item:
            return jsonify({"success": False, "message": "Item not found!"}), 404

        item_cost = item[0]

        if user_points < item_cost:
            return jsonify({"success": False, "message": "Not enough points to redeem this item!"}), 400

        # ✅ Deduct points and record redemption
        new_points = user_points - item_cost
        cursor.execute("UPDATE users SET points=? WHERE username=?", (new_points, session["username"]))
        cursor.execute("INSERT INTO redeemed_items (username, item_name) VALUES (?, ?)", (session["username"], item_name))

        conn.commit()  # ✅ Ensure transaction is committed

    return jsonify({"success": True, "message": f"Successfully redeemed {item_name}!", "remaining_points": new_points})




@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    username = data.get("username")
    new_password = data.get("newPassword")

    if not username or not new_password:
        return jsonify({"success": False, "message": "Username and new password are required!"}), 400

    conn = db_connection()
    cursor = conn.cursor()

    # Check if the user exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return jsonify({"success": False, "message": "User not found!"}), 404

    # Update password
    cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Password successfully reset!"})

if __name__ == '__main__':
    app.run(debug=True)


