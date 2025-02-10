Feature: Acceptance Testing for LBPS

	Scenario: Successful Admin Login
		Given Chrome browser is Launched
		When Open LBPS Login page
		Then Input Username "admin_user" and Password "adminpass"
		Then Click the login button
		Then Close Browser

	Scenario: Successful Student Login
		Given Chrome browser is Launched
		When Open LBPS Login page
		Then Input Username "student_user" and Password "studentpass"
		Then Click the login button
		Then Close Browser

	Scenario: Failed Login with Wrong Password
		Given Chrome browser is Launched
		When Open LBPS Login page
		Then Input Username "admin_user" and Password "wrongpass"
		Then Click the login button
		Then Close Browser