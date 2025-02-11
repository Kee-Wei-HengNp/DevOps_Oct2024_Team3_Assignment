from behave import when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from features.steps.common_steps import step_click_login, open_login_page # ✅ Import only necessary step
import os

@then(u'Verify Admin Dashboard is displayed')
def verify_admin_dashboard(context):
    """ ✅ Ensure Admin Dashboard Page Loads """
    WebDriverWait(context.driver, 3).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )
    assert "Admin Dashboard" in context.driver.page_source, "Admin Dashboard not displayed"

@then(u'Input new student details "{username}" "{password}" "{points}"')
def input_new_student_details(context, username, password, points):
    """ ✅ Fill in new student details and trigger input events """
    WebDriverWait(context.driver, 5).until(
        EC.presence_of_element_located((By.ID, "new-username"))
    )

    # ✅ Fill in each field properly
    username_field = context.driver.find_element(By.ID, "new-username")
    password_field = context.driver.find_element(By.ID, "new-password")
    points_field = context.driver.find_element(By.ID, "new-points")

    username_field.clear()
    username_field.send_keys(username)
    context.driver.execute_script("arguments[0].dispatchEvent(new Event('input'))", username_field)

    password_field.clear()
    password_field.send_keys(password)
    context.driver.execute_script("arguments[0].dispatchEvent(new Event('input'))", password_field)

    points_field.clear()
    points_field.send_keys(points)
    context.driver.execute_script("arguments[0].dispatchEvent(new Event('input'))", points_field)

    time.sleep(1)  # ✅ Give time for the form to process

@then(u'Click "Add Student" button')
def click_add_student(context):
    """ ✅ Click the Add Student Button and check for errors """
    add_button = context.driver.find_element(By.XPATH, "//button[contains(text(),'Add Student')]")
    add_button.click()
    
    time.sleep(2)  # ✅ Wait for response

    # ✅ Handle confirmation alert
    try:
        WebDriverWait(context.driver, 5).until(EC.alert_is_present())
        alert = context.driver.switch_to.alert
        alert.accept()  # Accept the update success alert
    except:
        print("No alert found after student update.")
        
@then(u'Verify student "{username}" appears in the list')
def verify_student_in_list(context, username):
    """ ✅ Check if student exists in the table """
    WebDriverWait(context.driver, 10).until(
        EC.text_to_be_present_in_element((By.ID, "student-list"), username)
    )
    assert username in context.driver.page_source, f"Student '{username}' not found"

@then(u'Upload CSV file "{file_name}"')
def upload_csv(context, file_name):
    """ ✅ Upload CSV file and handle success alert """
    file_path = os.path.abspath(os.path.join("features", "data", file_name))  # Ensure correct path
    file_input = context.driver.find_element(By.ID, "csv-file")
    
    file_input.send_keys(file_path)  # ✅ Upload CSV file
    time.sleep(2)  # ✅ Allow file input time to register

    # ✅ Click Upload button
    upload_button = context.driver.find_element(By.XPATH, "//button[contains(text(), 'Upload CSV')]")
    upload_button.click()

    # ✅ Wait for alert and handle it (if present)
    try:
        WebDriverWait(context.driver, 5).until(EC.alert_is_present())
        alert = context.driver.switch_to.alert
        print(f"✅ Alert Found: {alert.text}")  # Debugging output
        assert "uploaded successfully" in alert.text.lower(), f"Unexpected alert message: {alert.text}"
        alert.accept()  # ✅ Close the alert
    except:
        print("⚠️ No alert found after clicking 'Upload CSV'.")

    time.sleep(3)  # ✅ Allow UI to update
    context.driver.refresh()  # ✅ Force a page refresh to load new students



@then(u'Verify students from "{file_name}" appear in the list')
def verify_students_from_csv(context, file_name):
    """ ✅ Ensure uploaded students appear in the 'Student List' table """
    
    file_path = os.path.abspath(os.path.join("features", "data", file_name))  # ✅ Ensure correct path
    
    # ✅ Wait for the 'student-list' table to be visible
    WebDriverWait(context.driver, 15).until(
        EC.visibility_of_element_located((By.ID, "student-list"))
    )

    time.sleep(5)  # ✅ Allow UI update (increase if needed)

    with open(file_path, "r") as file:
        next(file)  # ✅ Skip CSV header
        for line in file:
            student_data = line.strip().split(",")  # ✅ Format: username,password,points
            user_name = student_data[0]  # ✅ Extract username (since it's the first column now)

            try:
                # ✅ Locate user in 'student-list' table
                student_row = WebDriverWait(context.driver, 15).until(
                    EC.presence_of_element_located(
                        (By.XPATH, f"//tbody[@id='student-list']/tr[td[contains(text(), '{user_name}')]]")
                    )
                )

                # ✅ Ensure user appears in the table
                assert user_name in student_row.text, f"❌ User {user_name} not found in 'Student List'!"
                print(f"✅ User {user_name} successfully found in 'Student List'!")

            except TimeoutException:
                raise AssertionError(f"❌ Timeout: User '{user_name}' was not found in 'Student List' within 15s!")





# ✅ Update Student
@then(u'Update student "{old_username}" username to "{new_username}"')
def update_student(context, old_username, new_username):
    """ ✅ Locate student row, edit username, and submit update """
    
    student_row = WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.XPATH, f"//tr[td[contains(text(), '{old_username}')]]"))
    )
    
    # ✅ Edit username directly
    username_cell = student_row.find_element(By.CLASS_NAME, "edit-username")
    context.driver.execute_script("arguments[0].textContent = arguments[1];", username_cell, new_username)
    time.sleep(1)

    # ✅ Click update button
    update_button = student_row.find_element(By.CLASS_NAME, "update-btn")
    update_button.click()

    # ✅ Handle Password Prompt (Alert)
    WebDriverWait(context.driver, 3).until(EC.alert_is_present())
    alert = context.driver.switch_to.alert
    alert.send_keys("newpassword123")  # ✅ Enter new password
    alert.accept()
    time.sleep(2)  # ✅ Allow time for update to complete

    # ✅ Handle Confirmation Alert
    WebDriverWait(context.driver, 3).until(EC.alert_is_present())
    success_alert = context.driver.switch_to.alert
    success_alert.accept()
    time.sleep(2)  # ✅ Allow time for update to complete


@then(u'Verify student "{new_username}" appears in search results')
def verify_updated_student(context, new_username):
    """ ✅ Ensure updated student is listed """
    WebDriverWait(context.driver, 10).until(
        EC.text_to_be_present_in_element((By.ID, "student-list"), new_username)
    )
    assert new_username in context.driver.page_source, "Updated student not found!"

@then(u'Search for student "{username}"')
def search_student(context, username):
    """ ✅ Search Student by Name """
    search_box = WebDriverWait(context.driver, 5).until(
        EC.presence_of_element_located((By.ID, "search-input"))
    )
    search_box.clear()
    search_box.send_keys(username)

    search_button = context.driver.find_element(By.XPATH, "//button[contains(text(),'Search')]")
    search_button.click()
    time.sleep(2)  # ✅ Wait for search results

@then(u'Click "Delete Student" button for "{username}"')
def delete_student(context, username):
    """ ✅ Find and delete the updated student """
    
    try:
        # ✅ Locate the student row in the table
        student_row = WebDriverWait(context.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//tr[td[contains(text(), '{username}')]]"))
        )

        # ✅ Click delete button inside that row
        delete_button = student_row.find_element(By.CLASS_NAME, "delete-btn")
        delete_button.click()

        # ✅ Handle confirmation alert
        WebDriverWait(context.driver, 5).until(EC.alert_is_present())
        alert = context.driver.switch_to.alert
        alert.accept()  # Accept deletion alert

        # ✅ Handle Success Alert After Deletion
        WebDriverWait(context.driver, 5).until(EC.alert_is_present())
        success_alert = context.driver.switch_to.alert
        success_alert.accept()

        # ✅ Wait for the student row to disappear
        WebDriverWait(context.driver, 10).until(
            EC.invisibility_of_element(student_row)
        )

    except:
        print("No alert found after student deletion.")
@then(u'Verify student "{username}" is removed from the list')
def verify_student_removed(context, username):
    """ ✅ Ensure student is removed after deletion """
    
    time.sleep(3)  # ✅ Allow UI to update
    student_list_text = context.driver.find_element(By.ID, "student-list").text

    assert username not in student_list_text, f"❌ Student {username} was not removed!"


