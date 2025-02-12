from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# ✅ Import necessary steps from common_steps.py & student_dashboard.py
from features.steps.common_steps import (
    launchChromeBrowser,
    open_login_page,
    step_input_credentials,
    step_click_login,
    verify_student_dashboard,
    click_logout,
    closeBrowser
)

from features.steps.student_dashboard_steps import (
    click_redeemable_items,
    click_redeemed_items
)

# ✅ Navigate to Redeemable Items Page
@given(u'The student is on the redeemable items page')
def navigate_to_redeemable_items_page(context):
    """ ✅ Redirects student to Redeemable Items page """
    click_redeemable_items(context)  # ✅ Use imported step instead of duplicating logic
    WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

# ✅ Click Redeem Button for an Item
@when(u'User clicks redeem for "{item_name}"')
def click_redeem_button(context, item_name):
    """ ✅ Click the redeem button for a given item and handle alert """
    try:
        # ✅ Ensure page is loaded
        WebDriverWait(context.driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )

        # ✅ Find and click the redeem button
        redeem_button = WebDriverWait(context.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//li[contains(.,'{item_name}')]/button"))
        )
        redeem_button.click()

        # ✅ Handle the JavaScript confirmation pop-up
        WebDriverWait(context.driver, 3).until(EC.alert_is_present())  # Wait for alert to appear
        alert = context.driver.switch_to.alert
        alert.accept()  # ✅ Click OK to confirm redemption
        time.sleep(2)  # ✅ Allow time for redemption to process

        # ✅ Handle success alert after redemption
        WebDriverWait(context.driver, 3).until(EC.alert_is_present())  # Wait for alert to appear
        alert = context.driver.switch_to.alert
        print(f"✅ Alert Text: {alert.text}")  # Debugging output
        alert.accept()  # ✅ Dismiss alert

        # ✅ Refresh the page before attempting next redemption
        context.driver.refresh()
        WebDriverWait(context.driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )

    except Exception as e:
        print(f"❌ Error during redemption for {item_name}: {e}")  # Log error if any



@then(u'Click "Back to Student Dashboard"')
def click_back_to_dashboard(context):
    """ ✅ Click Back to Student Dashboard and wait for the page to load. """
    back_button = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Back to Student Dashboard"))
    )
    back_button.click()

    # ✅ Ensure Student Dashboard loads before proceeding
    WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "student-container"))
    )
    assert "Student Dashboard" in context.driver.title, "❌ Student Dashboard did not load after clicking Back!"

