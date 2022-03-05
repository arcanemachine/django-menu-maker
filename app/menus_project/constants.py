from django.conf import settings
import server_config

FRONTEND_SERVER_URL = server_config.FRONTEND_SERVER_URL
FRONTEND_SERVER_URL_CONFIRM_EMAIL = \
    FRONTEND_SERVER_URL + '/register/confirm-email/'

# misc
PROJECT_NAME = "Menu Maker"
RESERVED_KEYWORDS = ['add-new-restaurant', 'all', 'delete', 'edit', 'new-item',
                     'new-section']

# validation #
MAX_RESTAURANTS_PER_USER = 3

# forms
FORMS_CAPTCHA_FIELD_HELP_TEXT = \
    "Please enter the letters seen in the image above."

# testing
TEST_USER_USERNAME = 'test_user'
TEST_USER_FIRST_NAME = 'Test'
TEST_USER_LAST_NAME = 'User'
TEST_USER_EMAIL = 'test_user@email.com'
TEST_USER_PASSWORD = 'my_password321'
RESTAURANT_ADMIN_USER_USERNAME = 'restaurant_admin'
TEST_RESTAURANT_NAME = 'Test Restaurant'
TEST_MENU_NAME = 'Test Menu'
TEST_MENUSECTION_NAME = 'Test Menu Section'
TEST_MENUITEM_NAME = 'Test Menu Item'
TEST_MENUITEM_DESCRIPTION = 'Test Menu Item Description'

# STRINGS #

# misc
RESERVED_KEYWORD_ERROR_STRING = \
    "This name is reserved and cannot be used. Please choose another name."

# restaurants
MAX_RESTAURANTS_PER_USER_ERROR_STRING = "You cannot register more than "\
    f"{MAX_RESTAURANTS_PER_USER} restaurants. If you wish to register a "\
    "new restaurant, you must first delete one of your existing restaurants."
RESTAURANT_DUPLICATE_SLUG_ERROR_STRING = \
    "This name is too similar to an existing restaurant name."

# users - registration
USER_REGISTER_ALREADY_AUTHENTICATED_MESSAGE = "You are already logged in, "\
    "so we redirected you here from the registration page."
if settings.EMAIL_CONFIRMATION_REQUIRED:
    USER_REGISTER_SUCCESS_MESSAGE = "Registration successful. Please "\
        "check your email inbox for your confirmation email."
else:
    USER_REGISTER_SUCCESS_MESSAGE = "Registration successful. "\
        "You may now login to your account."

# users - activation
USER_IS_UNCONFIRMED_MESSAGE = "You need to confirm your email address using "\
    "the activation link we sent to your inbox (check the spam folder too)."
USER_ACTIVATION_VIEW_MESSAGE = \
    "Please login to your account to complete the activation process."
USER_ACTIVATION_INVALID_URL_MESSAGE = "This validation URL is invalid."
USER_ACTIVATION_SUCCESS_MESSAGE = \
    "Your account has been successfully activated."

# users - authentication
USER_LOGIN_ALREADY_AUTHENTICATED_MESSAGE = \
    "You are already logged in, so we redirected you here from the login page."
USER_LOGIN_SUCCESS_MESSAGE = "You have successfully logged in."
USER_LOGOUT_SUCCESS_MESSAGE = "You have successfully logged out."
USER_UPDATE_SUCCESS_MESSAGE = "You have updated your personal information."
USER_DELETE_SUCCESS_MESSAGE = "Your account has been deleted."
