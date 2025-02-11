import unittest
import json
from app import app, get_user_from_db, students, redeemable_items, db_connection, random

class FlaskAppTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the test client before running tests."""
        app.config['TESTING'] = True
        cls.client = app.test_client()  # ✅ Define `cls.client` before using it

        # ✅ Ensure test users exist in the database before running tests
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, 'admin')",
                    ("admin_user", "adminpass"))
        cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, 'student')",
                    ("student_user", "studentpass"))
        conn.commit()
        conn.close()

        # ✅ Move session setup inside a separate transaction
        with cls.client.session_transaction() as sess:
            sess["username"] = "admin_user"
            sess["role"] = "admin"



    ### ✅ TEST HOME PAGE LOAD ###
    def test_home_route(self):
        """Test if the login page loads correctly."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Login", response.data)

    ### ✅ TEST LOGIN FUNCTIONALITY ###
    def test_get_user_from_db(self):
        """Test database user retrieval function."""
        user = get_user_from_db('admin_user')  # Ensure 'admin_user' exists in DB
        self.assertIsNotNone(user)
        self.assertEqual(user[0], 'admin_user')
        self.assertEqual(user[2], 'admin')  # Role should be 'admin'

    def test_login_success_admin(self):
        """Test successful login for an admin user."""
        response = self.client.post('/login', data=json.dumps({
            'username': 'admin_user',
            'password': 'adminpass'
        }), content_type='application/json')

        data = response.get_json()

        # ✅ Debug login response if test fails
        if response.status_code != 200:
            print(f"ADMIN LOGIN FAILED: {data}")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['redirect_url'], '/admin')


    def test_login_success_student(self):
        """Test successful login for a student user."""
        response = self.client.post('/login', data=json.dumps({
            'username': 'student_user',
            'password': 'studentpass'
        }), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['redirect_url'], '/student')

    def test_login_failure(self):
        """Test login failure with incorrect credentials."""
        response = self.client.post('/login', data=json.dumps({
            'username': 'invalid_user',
            'password': 'wrongpass'
        }), content_type='application/json')

        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertIn("Invalid username or password", data['message'])

    def test_login_missing_fields(self):
        """Test login failure due to missing username or password."""
        response = self.client.post('/login', data=json.dumps({
            'username': '',
            'password': ''
        }), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertIn("Username or password is missing!", data['message'])

    ### ✅ TEST STUDENT DASHBOARD ###
    def test_student_page(self):
        """Test if the student page loads correctly."""
        response = self.client.get('/student')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome,", response.data)
        self.assertIn(b"Total Points:", response.data)

    ### ✅ TEST ADMIN DASHBOARD ###
    def test_admin_page(self):
        """Test if the admin page loads correctly."""
        response = self.client.get('/admin', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Admin Dashboard", response.data)

    ### ✅ TEST REDEEMABLE ITEMS PAGE ###
    def test_redeemable_items_page(self):
        """Test if the redeemable items page loads correctly."""
        response = self.client.get('/redeemable-items')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Redeemable Items", response.data)

    ### ✅ TEST SUCCESSFUL REDEMPTION ###
    def test_redeem_item_success(self):
        """Test successful item redemption when enough points are available."""
        students["test_student"]["points"] = 1000  # Ensure enough points

        response = self.client.post('/redeem-item', data=json.dumps({
            "item": "AAA"  # AAA costs 200 points
        }), content_type='application/json')

        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["remaining_points"], 800)  # 1000 - 200 = 800

    ### ❌ TEST REDEMPTION FAILURE DUE TO INSUFFICIENT POINTS ###
    def test_redeem_item_insufficient_points(self):
        """Test redemption failure when user does not have enough points."""
        students["test_student"]["points"] = 100  # Not enough for any item

        response = self.client.post('/redeem-item', data=json.dumps({
            "item": "BBB"  # BBB costs 300 points
        }), content_type='application/json')

        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data["success"])
        self.assertIn("Not enough points", data["message"])

    ### ❌ TEST REDEMPTION FAILURE DUE TO INVALID ITEM ###
    def test_redeem_item_invalid(self):
        """Test redemption failure when item does not exist."""
        students["test_student"]["points"] = 500  # Ensure some points exist

        response = self.client.post('/redeem-item', data=json.dumps({
            "item": "ZZZ"  # This item does not exist
        }), content_type='application/json')

        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])
        self.assertIn("Item not found", data["message"])

    ### ✅ TEST REDEEMED ITEMS PAGE ###
    def test_redeemed_items_page(self):
        """Test if the redeemed items page loads correctly."""
        students["test_student"]["redeemed_items"] = ["AAA", "BBB"]

        response = self.client.get('/redeemed-items', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AAA", response.data)
        self.assertIn(b"BBB", response.data)

    ### ✅ TEST ADD STUDENT ###
    def test_add_student(self):
        """Test adding a student via admin panel."""
        unique_username = f"test_student_{random.randint(1000, 9999)}"  # Generate unique username

        response = self.client.post('/add_student', data=json.dumps({
            "username": unique_username,
            "password": "testpassword",
            "points": 500  # ✅ Ensure points field is sent
        }), content_type='application/json')

        data = response.get_json()

        # ✅ Debug API response if test fails
        if not data["success"]:
            print(f"ADD STUDENT API RESPONSE: {data}")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "Student added successfully!")



    ### ✅ TEST DELETE STUDENT ###
    def test_delete_student(self):
        """Test deleting a student via admin panel."""
        response = self.client.post('/delete-student', data=json.dumps({
            "id": 1
        }), content_type='application/json')

        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "Student deleted successfully!")

    ### ✅ Test password reset for a specific user ###
    def test_reset_password(self):
        response = self.client.post('/reset-password', data=json.dumps({
            "username": "student_user",
            "old_password": "studentpass",
            "new_password": "newpass123"
        }), content_type='application/json')

        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], "Password reset successful")

        #Verify login with new password
        login_response = self.client.post('/login', data=json.dumps({
            "username": "student_user",
            "password": "newpass123"
        }), content_type='application/json')

        self.assertEqual(login_response.status_code, 200)
        self.assertTrue(login_response.get_json()["success"])

if __name__ == '__main__':
    unittest.main()
