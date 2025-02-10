from behave import *
from features.steps.common_steps import step_click_login, closeBrowser # ✅ Import shared steps
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

# Configure logging
logging.basicConfig(filename="test_results.log", level=logging.INFO, format="%(asctime)s - %(message)s")

@when(u'Open "{page}" directly')
def openPageDirectly(context, page):
    context.driver.get(f"http://127.0.0.1:5000{page}")
    time.sleep(2)

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

@then(u'Verify login page elements are visible')
def verifyLoginElements(context):
    wait = WebDriverWait(context.driver, 10)
    try:
        wait.until(EC.visibility_of_element_located((By.ID, "username")))
        wait.until(EC.visibility_of_element_located((By.ID, "password")))
        wait.until(EC.visibility_of_element_located((By.ID, "login-btn")))
        logging.info("✅ Login Page Elements Verified")
    except:
        assert False, "Login page elements not visible!"

@then(u'Verify error message "{error_msg}"')
def verifyErrorMessage(context, error_msg):
    wait = WebDriverWait(context.driver, 5)
    error_element = wait.until(EC.visibility_of_element_located((By.ID, "error-message")))
    actual_error = error_element.text

    assert actual_error == error_msg, f"Expected '{error_msg}', but got '{actual_error}'"
    logging.info(f"✅ Error Message Verified: {actual_error}")


# ✅ Add Empty Credentials Step Here
@then(u'Input Username "" and Password ""')
def step_input_empty_credentials(context):
    username_field = context.driver.find_element(By.ID, "username")
    password_field = context.driver.find_element(By.ID, "password")

    username_field.clear()  # ✅ Keep field empty
    password_field.clear()  # ✅ Keep field empty

    time.sleep(2)  # ✅ Allow UI to reflect changes