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

# Dummy student data (for now, this will be replaced with actual user sessions later)
students = {
    "test_student": {"points": random.randint(500, 9999)}
}

# Dummy redeemable items (fixed list for now)
redeemable_items = [
    {"name": "AAA", "cost": 200},
    {"name": "BBB", "cost": 300},
    {"name": "CCC", "cost": 400}
]

@app.route('/redeemable-items')
def redeemable_items_page():
    """Display available redeemable items."""
    user = students["test_student"]  # Simulated logged-in student
    return render_template('redeemable_items.html', items=redeemable_items, points=user["points"])


@app.route('/redeemed-items')
def redeemed_items():
    return render_template('redeemed_items.html')


@app.route('/recover-password')
def recover_password():
    return render_template('recover_password.html')


@app.route('/redeem-item', methods=['POST'])
def redeem_item():
    """Handle item redemption."""
    data = request.json
    item_name = data.get("item")

    user = students["test_student"]  # Simulated logged-in student
    user_points = user["points"]

    # Find the item
    item = next((i for i in redeemable_items if i["name"] == item_name), None)

    if not item:
        return jsonify({"success": False, "message": "Item not found!"}), 404

    if user_points < item["cost"]:
        return jsonify({"success": False, "message": "Not enough points to redeem this item!"}), 400

    # Deduct points and confirm redemption
    user["points"] -= item["cost"]
    return jsonify({"success": True, "message": f"Successfully redeemed {item_name}!", "remaining_points": user["points"]})

if __name__ == '__main__':
    app.run(debug=True)


