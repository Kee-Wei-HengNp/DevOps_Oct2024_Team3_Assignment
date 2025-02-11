Feature: Redeemable Items Testing

	Background:
		Given Chrome browser is Launched
		When Open LBPS Login page
		Then Input Username "student_user" and Password "studentpass"
		Then Click the login button
		Then Verify Student Dashboard is displayed

	Scenario: Successfully redeem an item within available points
		Given The student is on the redeemable items page
		When User clicks redeem for "BBB"

	Scenario: Attempt to redeem an item with insufficient points
		Given The student is on the redeemable items page
		When User clicks redeem for "CCC"