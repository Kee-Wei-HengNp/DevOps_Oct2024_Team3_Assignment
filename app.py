from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

users = {
    "testuser": "password123",
    "exampleuser": "securepass"
}

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

    if username in users and users[username] == password:
        return jsonify({"success": True, "message": "Login successful!"})
    else:
        return jsonify({"success": False, "message": "Invalid username or password"}), 401

if __name__ == '__main__':
    app.run(debug=True)
