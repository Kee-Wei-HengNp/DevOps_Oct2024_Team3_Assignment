from behave import then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# ✅ Import necessary steps from common_steps.py to avoid redundancy
from features.steps.common_steps import (
    launchChromeBrowser,
    open_login_page,
    step_input_credentials,
    step_click_login,
    verifyRedirectToLogin,
    verify_student_dashboard,
    click_logout,
    closeBrowser
)



@then(u'Verify student name "{expected_username}" is displayed')
def verify_student_name(context, expected_username):
    """ ✅ Check if correct student username is displayed """
    displayed_username = WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    ).text
    assert displayed_username == expected_username, f"❌ Expected '{expected_username}', but got '{displayed_username}'"

@then(u'Click on Redeemable Items')
def click_redeemable_items(context):
    """ ✅ Click Redeemable Items """
    redeemable_link = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Redeemable Items"))
    )
    redeemable_link.click()
    time.sleep(2)

@then(u'Click on Redeemed Items')
def click_redeemed_items(context):
    """ ✅ Click Redeemed Items """
    redeemed_link = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Redeemed Items"))
    )
    redeemed_link.click()
    time.sleep(2)

@then(u'Verify user is redirected to "{expected_page}"')
def verify_page_redirect(context, expected_page):
    """ ✅ Verify user lands on the correct page after clicking """
    time.sleep(2)  # ✅ Allow page load
    assert expected_page in context.driver.title, f"❌ Expected {expected_page}, but got {context.driver.title}"


