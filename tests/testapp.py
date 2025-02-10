import unittest
import json
from app import app, get_user_from_db, students, redeemable_items


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
        user = get_user_from_db(
            'admin_user')  # Ensure 'admin_user' exists in the database
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
        self.assertEqual(response.status_code, 200)  # Page should load
        self.assertIn(b"Welcome,", response.data)  # Partial match for username
        # Ensure points are displayed
        self.assertIn(b"Total Points:", response.data)

    def test_admin_page(self):
        """Test if the admin page loads correctly."""
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome to the Admin Page!", response.data)

    def test_redeemable_items_page(self):
        """Test if the redeemable items page loads correctly."""
        response = self.client.get('/redeemable-items')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Redeemable Items", response.data)  # Page title check

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

    def test_redeemed_items_page(self):
        """Test if the redeemed items page loads correctly."""
        response = self.client.get('/redeemed-items')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Redeemed Items", response.data)  # Check page title
        # Placeholder text
        self.assertIn(
            b"This page will display items that the student has already redeemed.", response.data)
        
    ### ✅ TEST REDEEMED ITEMS PAGE (NO ITEMS) ###
    def test_redeemed_items_page_no_items(self):
        """Test if the redeemed items page shows the correct message when no items are redeemed."""
        students["test_student"]["redeemed_items"] = []  # No redeemed items

        response = self.client.get('/redeemed-items')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"You have not redeemed any items yet.", response.data)
        
    ### ✅ TEST REDEEMED ITEMS PAGE (WITH ITEMS) ###
    def test_redeemed_items_page_with_items(self):
        """Test if the redeemed items page correctly displays redeemed items."""
        students["test_student"]["redeemed_items"] = ["AAA", "BBB"]  # Some redeemed items

        response = self.client.get('/redeemed-items')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AAA", response.data)
        self.assertIn(b"BBB", response.data)
        
    ### ✅ TEST REDEMPTION AND DISPLAY ###
    def test_redeem_and_display(self):
        """Test redeeming an item and verifying it appears on the redeemed items page."""
        students["test_student"]["points"] = 500  # Ensure enough points
        students["test_student"]["redeemed_items"] = []  # Start with empty list

        # Redeem item "AAA"
        response = self.client.post('/redeem-item', data=json.dumps({
            "item": "AAA"
        }), content_type='application/json')

        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(students["test_student"]["points"], 300)  # 500 - 200 = 300

        # Check that "AAA" is now in redeemed items
        response = self.client.get('/redeemed-items')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AAA", response.data)


if __name__ == '__main__':
    unittest.main()
