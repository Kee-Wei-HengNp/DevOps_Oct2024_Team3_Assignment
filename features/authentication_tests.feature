Feature: Authentication Testing

	Scenario: Failed Login with Empty Fields
		Given Chrome browser is Launched
		When Open LBPS Login page
		Then Input Username "" and Password ""
		Then Click the login button
		Then Verify error message "Username or password is missing!"
		Then Close Browser

	Scenario: Directly Access Admin Page Without Login
		Given Chrome browser is Launched
		When Open "/admin" directly
		Then Verify user is redirected to Login Page
		Then Close Browser

	Scenario: Directly Access Student Page Without Login
		Given Chrome browser is Launched
		When Open "/student" directly
		Then Verify user is redirected to Login Page
		Then Close Browser
