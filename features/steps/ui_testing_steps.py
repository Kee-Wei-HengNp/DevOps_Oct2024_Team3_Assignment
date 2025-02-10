from behave import *
from features.steps.common_steps import launchChromeBrowser  # ✅ Import shared WebDriver setup
from selenium.webdriver.common.by import By
import time

@when(u'Open LBPS Login page')
def openLBPSPage(context):
    context.driver.get("http://127.0.0.1:5000/")  # ✅ Ensure this is correct
    time.sleep(2)

