import unittest
import json
from app import app, get_user_from_db, redeemable_items, db_connection, random

class FlaskAppTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up the test client before running tests."""
        app.config['TESTING'] = True
        cls.client = app.test_client()
        
        cls.create_test_user("admin_user", "adminpass", "admin")
        cls.create_test_user("student_user", "studentpass", "student")
    
    @classmethod
    def create_test_user(cls, username, password, role, points=1000):
        """Helper function to create a test user in the database."""
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO users (username, password, role, points) VALUES (?, ?, ?, ?)",
                       (username, password, role, points))
        conn.commit()
        conn.close()
    
    @classmethod
    def cleanup_test_user(cls, username):
        """Helper function to remove a test user from the database."""
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username=?", (username,))
        conn.commit()
        conn.close()

    def setUp(self):
        """Runs before each test case."""
        self.create_test_user("test_student", "testpass", "student", 1000)
    
    def tearDown(self):
        """Runs after each test case."""
        self.cleanup_test_user("test_student")

    ### ✅ TEST HOME PAGE LOAD ###
    def test_home_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Login", response.data)

    ### ✅ TEST DATABASE USER RETRIEVAL ###
    def test_get_user_from_db(self):
        """Test database user retrieval function."""
        user = get_user_from_db("admin_user")
        self.assertIsNotNone(user)
        self.assertEqual(user[0], "admin_user")
        self.assertEqual(user[2], "admin")


    ### ✅ TEST ADMIN PAGE ###
    def test_admin_page(self):
        """Test if the admin page loads correctly."""
        with self.client.session_transaction() as sess:
            sess["username"] = "admin_user"
            sess["role"] = "admin"
        
        response = self.client.get('/admin', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Admin Dashboard", response.data)


    ### ✅ TEST LOGIN FUNCTIONALITY ###
    def test_login_success_admin(self):
        response = self.client.post('/login', data=json.dumps({
            'username': 'admin_user',
            'password': 'adminpass'
        }), content_type='application/json')
        
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['redirect_url'], '/admin')

    def test_login_success_student(self):
        response = self.client.post('/login', data=json.dumps({
            'username': 'student_user',
            'password': 'studentpass'
        }), content_type='application/json')
        
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['redirect_url'], '/student')
    
    def test_login_failure(self):
        response = self.client.post('/login', data=json.dumps({
            'username': 'invalid_user',
            'password': 'wrongpass'
        }), content_type='application/json')
        
        self.assertEqual(response.status_code, 401)

        ### ✅ TEST LOGIN FAILURE DUE TO MISSING FIELDS ###
    def test_login_missing_fields(self):
        """Test login failure due to missing username or password."""
        response = self.client.post('/login', data=json.dumps({
            "username": "",
            "password": ""
        }), content_type='application/json')

        self.assertEqual(response.status_code, 400)

    
    def test_logout(self):
        with self.client.session_transaction() as sess:
            sess["username"] = "admin_user"
            sess["role"] = "admin"
        
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Login", response.data)
    
    ### ✅ TEST STUDENT DASHBOARD ###
    def test_student_page(self):
        with self.client.session_transaction() as sess:
            sess["username"] = "test_student"
            sess["role"] = "student"
        
        response = self.client.get('/student', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome,", response.data)
    
    ### ✅ TEST REDEEMABLE ITEMS PAGE ###
    def test_redeemable_items_page(self):
        with self.client.session_transaction() as sess:
            sess["username"] = "test_student"
            sess["role"] = "student"
        
        response = self.client.get('/redeemable-items', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Redeemable Items", response.data)

    ### ✅ TEST REDEEMED ITEMS PAGE ###
    def test_redeemed_items_page(self):
        """Test if the redeemed items page loads correctly."""
        conn = db_connection()
        cursor = conn.cursor()

        # ✅ Ensure test student exists
        cursor.execute("INSERT OR REPLACE INTO users (username, password, role, points) VALUES (?, ?, 'student', ?)",
                    ("test_student", "testpass", 500))
        conn.commit()

        # ✅ Simulate item redemption
        cursor.execute("INSERT INTO redeemed_items (username, item_name) VALUES (?, ?)", ("test_student", "AAA"))
        cursor.execute("INSERT INTO redeemed_items (username, item_name) VALUES (?, ?)", ("test_student", "BBB"))
        conn.commit()
        conn.close()

        with self.client.session_transaction() as sess:
            sess["username"] = "test_student"
            sess["role"] = "student"

        response = self.client.get('/redeemed-items', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AAA", response.data)
        self.assertIn(b"BBB", response.data)

    
    ### ✅ TEST SUCCESSFUL REDEMPTION ###
    def test_redeem_item_success(self):
        with self.client.session_transaction() as sess:
            sess["username"] = "test_student"
            sess["role"] = "student"
        
        response = self.client.post('/redeem-item', data=json.dumps({
            "item": "AAA"
        }), content_type='application/json')
        
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])

    ### ✅ TEST REDEEM ITEM INVALID (NON-EXISTENT ITEM) ###
    def test_redeem_item_invalid(self):
        """Test redemption failure when item does not exist."""
        with self.client.session_transaction() as sess:
            sess["username"] = "test_student"
            sess["role"] = "student"

        response = self.client.post('/redeem-item', data=json.dumps({
            "item": "ZZZ"  # This item does not exist
        }), content_type='application/json')

        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])

    
    ### ❌ TEST REDEMPTION FAILURE DUE TO INSUFFICIENT POINTS ###
    def test_redeem_item_insufficient_points(self):
        self.create_test_user("low_points_student", "testpass", "student", 50)
        with self.client.session_transaction() as sess:
            sess["username"] = "low_points_student"
            sess["role"] = "student"
        
        response = self.client.post('/redeem-item', data=json.dumps({"item": "AAA"}), content_type='application/json')
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data["success"])
        self.cleanup_test_user("low_points_student")
    
    ### ✅ TEST ADD STUDENT ###
    def test_add_student(self):
        unique_username = f"test_student_{random.randint(1000, 9999)}"
        response = self.client.post('/add_student', data=json.dumps({
            "username": unique_username,
            "password": "testpassword",
            "points": 500
        }), content_type='application/json')
        
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])

    ### ✅ TEST DELETE STUDENT ###
    def test_delete_student(self):
        """Test deleting a student via admin panel."""
        unique_username = f"delete_student_{random.randint(1000, 9999)}"
        self.create_test_user(unique_username, "testpass", "student", 500)

        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=?", (unique_username,))
        student_data = cursor.fetchone()

        # ✅ Debugging Output: Print all users if the student is not found
        if not student_data:
            cursor.execute("SELECT * FROM users")
            all_users = cursor.fetchall()
            print(f"DEBUG: User table contents in CI/CD: {all_users}")
            self.fail("Student ID retrieval failed before deletion test")

        student_id = student_data[0]
        conn.close()

        response = self.client.post('/delete-student', data=json.dumps({
            "id": student_id
        }), content_type='application/json')

        data = response.get_json()
        if response.status_code != 200:
            print(f"DELETE STUDENT FAILED: {data}")

        self.assertEqual(response.status_code, 200)




    
if __name__ == '__main__':
    unittest.main()
