Feature: Admin Dashboard Testing

	Background:
		Given Chrome browser is Launched
		When Open LBPS Login page
		Then Input Username "admin_user" and Password "adminpass"
		Then Click the login button
		Then Verify Admin Dashboard is displayed

	Scenario: Add a new student
		Then Input new student details "test_student" "password123" "100"
		Then Click "Add Student" button
		Then Verify student "test_student" appears in the list

	Scenario: Upload CSV File to Add Multiple Students
		Then Upload CSV file "students.csv"
		Then Verify students from "students.csv" appear in the list

	Scenario: Update student details
		Then Update student "test_student" username to "updated_student"
		Then Verify student "updated_student" appears in search results

	Scenario: Search for a student
		Then Search for student "updated_student"
		Then Verify student "updated_student" appears in search results

	Scenario: Delete a student
		Then Click "Delete Student" button for "updated_student"
		Then Verify student "updated_student" is removed from the list

	Scenario: Logout from Admin Dashboard
		Then Click Logout button
		Then Verify user is redirected to Login Page
