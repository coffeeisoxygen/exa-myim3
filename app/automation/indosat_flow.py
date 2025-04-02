import logging

from app.ui.actions import ClickAction, InputTextAction, WaitForElementAction
from app.ui.element import Element
from app.ui.flow import UIFlow

logger = logging.getLogger(__name__)

# Define common UI elements
LOGIN_BUTTON = Element("Login Button", resource_id="com.pure.indosat.care:id/btnLogin")
PHONE_INPUT = Element("Phone Input", resource_id="com.pure.indosat.care:id/etMsisdn")
PASSWORD_INPUT = Element(
    "Password Input", resource_id="com.pure.indosat.care:id/etPassword"
)
SUBMIT_LOGIN = Element("Submit Login", resource_id="com.pure.indosat.care:id/btnSubmit")
OTP_INPUT = Element("OTP Input", resource_id="com.pure.indosat.care:id/otpView")
VERIFY_OTP = Element("Verify OTP", resource_id="com.pure.indosat.care:id/btnVerify")

# Add elements for the rest of your flow (topup, reseller, product selection, etc.)


def create_login_flow(phone_number: str, password: str) -> UIFlow:
    """Create a flow for logging into the Indosat app.

    Args:
        phone_number: Phone number to log in with
        password: Password for the account

    Returns:
        UIFlow for login process
    """
    login_flow = UIFlow("Login Flow")

    # Add actions for login
    login_flow.add_action(ClickAction("Click Login", LOGIN_BUTTON))
    login_flow.add_action(WaitForElementAction("Wait for Phone Input", PHONE_INPUT))
    login_flow.add_action(InputTextAction("Enter Phone", PHONE_INPUT, phone_number))
    login_flow.add_action(InputTextAction("Enter Password", PASSWORD_INPUT, password))
    login_flow.add_action(ClickAction("Submit Credentials", SUBMIT_LOGIN))

    return login_flow


def create_otp_verification_flow(otp: str) -> UIFlow:
    """Create a flow for OTP verification.

    Args:
        otp: One-time password to enter

    Returns:
        UIFlow for OTP verification
    """
    otp_flow = UIFlow("OTP Verification Flow")

    # Add actions for OTP verification
    otp_flow.add_action(WaitForElementAction("Wait for OTP Input", OTP_INPUT))
    otp_flow.add_action(InputTextAction("Enter OTP", OTP_INPUT, otp))
    otp_flow.add_action(ClickAction("Verify OTP", VERIFY_OTP))

    return otp_flow


# Continue implementing additional flows for each part of your purchase process
