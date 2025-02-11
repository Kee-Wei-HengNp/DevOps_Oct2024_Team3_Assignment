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

from features.steps.student_dashboard_steps import (
 verify_student_name,
 click_redeemed_items,
 verify_page_redirect
)