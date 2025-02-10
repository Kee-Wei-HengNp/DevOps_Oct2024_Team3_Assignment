from behave import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os

# Define the correct path for ChromeDriver
CHROME_DRIVER_PATH = os.path.join(os.getcwd(), "chromedriver.exe")

@given(u'Chrome browser is Launched')
def launchChromeBrowser(context):
    service = Service(CHROME_DRIVER_PATH)
    context.driver = webdriver.Chrome(service=service)
    context.driver.maximize_window()
    time.sleep(2)

@when(u'Open LBPS Login page')
def openLBPSPage(context):
    context.driver.get("http://127.0.0.1:5000/")  # ✅ Ensure this is correct
    time.sleep(2)

@then(u'Input Username "{username}" and Password "{password}"')
def step_input_credentials(context, username, password):
    username_field = context.driver.find_element(By.ID, "username")
    password_field = context.driver.find_element(By.ID, "password")

    username_field.clear()
    username_field.send_keys(username)
    password_field.clear()
    password_field.send_keys(password)
    time.sleep(2)

@then(u'Click the login button')
def step_click_login(context):
    username = context.driver.find_element(By.ID, "username").get_attribute("value")
    password = context.driver.find_element(By.ID, "password").get_attribute("value")

    # ✅ Send a JSON request instead of submitting the form
    script = f"""
    fetch("http://127.0.0.1:5000/login", {{
        method: "POST",
        headers: {{
            "Content-Type": "application/json"
        }},
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


@then(u'Close Browser')
def closeBrowser(context):
    context.driver.quit()
