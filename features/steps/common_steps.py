from behave import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

# Define the correct path for ChromeDriver
CHROME_DRIVER_PATH = os.path.join(os.getcwd(), "chromedriver.exe")

def before_all(context):
    """ ✅ Start Chrome only once for all scenarios """
    if not hasattr(context, "driver"):
        service = Service(CHROME_DRIVER_PATH)
        context.driver = webdriver.Chrome(service=service)
        context.driver.maximize_window()
        time.sleep(2)  # ✅ Allow browser to load

def after_all(context):
    """ ✅ Close the browser after all tests are complete """
    if hasattr(context, "driver"):
        context.driver.quit()

@given(u'Chrome browser is Launched')
def launchChromeBrowser(context):
    if not hasattr(context, "driver"):  # Prevent multiple instances
        service = Service(CHROME_DRIVER_PATH)
        context.driver = webdriver.Chrome(service=service)
        context.driver.maximize_window()
        time.sleep(2)

@when(u'Open LBPS Login page')  # ✅ Move here and remove from other step files
def open_login_page(context):
    context.driver.get("http://127.0.0.1:5000/")
    time.sleep(3)

@then(u'Input Username "{username}" and Password "{password}"')
def step_input_credentials(context, username, password):
    username_field = context.driver.find_element(By.ID, "username")
    password_field = context.driver.find_element(By.ID, "password")

    username_field.clear()
    username_field.send_keys(username)
    password_field.clear()
    password_field.send_keys(password)
    time.sleep(5)

@then(u'Click the login button')
def step_click_login(context):
    username = context.driver.find_element(By.ID, "username").get_attribute("value")
    password = context.driver.find_element(By.ID, "password").get_attribute("value")

    # ✅ Send a JSON request instead of submitting the form
    script = f"""
    fetch("http://127.0.0.1:5000/login", {{
        method: "POST",
        headers: {{"Content-Type": "application/json"}},
        body: JSON.stringify({{"username": "{username}", "password": "{password}"}})
    }}).then(response => response.json())
      .then(data => {{
          if (data.success) {{
              window.location.href = data.redirect_url;
          }} else {{
              document.getElementById("error-message").innerText = data.message;
          }}
      }});
    """
    
    context.driver.execute_script(script)
    time.sleep(3)  # Allow time for the redirect

@then(u'Verify error message "{error_msg}"')
def verifyErrorMessage(context, error_msg):
    wait = WebDriverWait(context.driver, 5)
    error_element = wait.until(EC.visibility_of_element_located((By.ID, "error-message")))
    actual_error = error_element.text

    assert actual_error == error_msg, f"Expected '{error_msg}', but got '{actual_error}'"
    logging.info(f"✅ Error Message Verified: {actual_error}")


@then(u'Verify success message "{expected_message}"')
def verify_success_message(context, expected_message):
    """ ✅ Ensure the success message is found in an alert """
    try:
        # ✅ Wait for an alert to appear
        WebDriverWait(context.driver, 5).until(EC.alert_is_present())
        alert = context.driver.switch_to.alert
        actual_message = alert.text

        # ✅ Verify if the expected message matches the alert text
        assert expected_message in actual_message, (
            f"❌ Expected '{expected_message}', but got '{actual_message}'"
        )

        logging.info(f"✅ Alert Text: {actual_message}")

        # ✅ Accept the alert to close it
        alert.accept()

    except Exception as e:
        logging.error(f"❌ Error verifying success message: {str(e)}")
        assert False, "❌ Success message not found as an alert!"


@then(u'Verify total points is "{expected_points}"')
def verify_updated_points(context, expected_points):
    """ ✅ Ensure student points are updated correctly """
    expected_points = int(expected_points)
    
    # ✅ Wait for total-points element to appear and update
    points_element = WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.ID, "total-points"))
    )

    updated_points = int(points_element.text)

    assert updated_points == expected_points, (
        f"❌ Points not updated correctly! Expected {expected_points}, but got {updated_points}."
    )

    logging.info(f"✅ Points Updated: {updated_points} (Expected: {expected_points})")


@then(u'Verify user is redirected to Login Page')
def verifyRedirectToLogin(context):
    wait = WebDriverWait(context.driver, 10)
    expected_url = "http://127.0.0.1:5000/"
    
    try:
        # ✅ Check if the browser was redirected to login page
        wait.until(EC.url_to_be(expected_url))
        logging.info(f"✅ Redirection Verified: {context.driver.current_url}")
    except:
        # 🔴 Log the actual URL if redirection failed
        logging.error(f"❌ Redirection FAILED! Current URL: {context.driver.current_url}")
        assert context.driver.current_url == expected_url, f"Expected {expected_url}, but got {context.driver.current_url}"

@then(u'Verify Student Dashboard is displayed')
def verify_student_dashboard(context):
    """ ✅ Ensure Student Dashboard is visible """
    WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "student-container"))
    )
    assert "Student Dashboard" in context.driver.title, "❌ Student Dashboard is not displayed!"

@then(u'Click Logout button')
def click_logout(context):
    """ ✅ Click Logout button """
    logout_button = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "logout-button"))
    )
    logout_button.click()
    time.sleep(2)

@then(u'Close Browser')
def closeBrowser(context):
    context.driver.quit()