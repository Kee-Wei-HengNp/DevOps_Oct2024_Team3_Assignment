Feature: Student Dashboard Testing

	Background:
		Given Chrome browser is Launched
		When Open LBPS Login page
		Then Input Username "student_user" and Password "studentpass"
		Then Click the login button
		Then Verify Student Dashboard is displayed
		Then Verify student name "student_user" is displayed

	Scenario: Navigate to Redeemable Items Page
		Then Click on Redeemable Items
		Then Verify user is redirected to "Redeemable Items"

	Scenario: Navigate to Redeemed Items Page
		Then Click on Redeemed Items
		Then Verify user is redirected to "Redeemed Items"

	Scenario: Logout from Student Dashboard
		Then Click Logout button
		Then Verify user is redirected to Login Page