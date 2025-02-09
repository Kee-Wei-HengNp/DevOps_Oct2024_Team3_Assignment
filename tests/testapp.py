import unittest
import json
from app import app, get_user_from_db

class FlaskAppTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the test client before running tests."""
        app.config['TESTING'] = True
        cls.client = app.test_client()

    def test_home_route(self):
        """Test if the login page loads correctly."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Login", response.data)

    def test_get_user_from_db(self):
        """Test database user retrieval function."""
        user = get_user_from_db('admin_user')  # Ensure 'admin_user' exists in the database
        self.assertIsNotNone(user)
        self.assertEqual(user[0], 'admin_user')
        self.assertEqual(user[2], 'admin')  # Role should be 'admin'

    def test_login_success_admin(self):
        """Test successful login for an admin user."""
        response = self.client.post('/login', data=json.dumps({
            'username': 'admin_user',
            'password': 'adminpass'
        }), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
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

def test_student_page(self):
    """Test if the student page loads correctly."""
    response = self.client.get('/student')
    self.assertEqual(response.status_code, 200)
    self.assertIn(b'<span id="username">', response.data)  # Ensures username is present


    def test_admin_page(self):
        """Test if the admin page loads correctly."""
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome to the Admin Page!", response.data)

if __name__ == '__main__':
    unittest.main()
