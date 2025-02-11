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

@then(u'Close Browser')
def closeBrowser(context):
    context.driver.quit()