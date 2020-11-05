# misc

PROJECT_NAME = "Menu Maker"
RESERVED_KEYWORDS = ['add-new-restaurant', 'all', 'delete', 'edit', 'new-item',
    'new-section']

# testing

TEST_USER_USERNAME = 'test_user'
TEST_USER_FIRST_NAME = 'Test'
TEST_USER_LAST_NAME = 'User'
TEST_USER_EMAIL = 'test_user@email.com'
TEST_USER_PASSWORD = 'test_user_password'
RESTAURANT_ADMIN_USER_USERNAME = 'restaurant_admin'
RESTAURANT_ADMIN_USER_PASSWORD = 'restaurant_admin_password'
TEST_RESTAURANT_NAME = 'Test Restaurant'
TEST_MENU_NAME = 'Test Menu'
TEST_MENUSECTION_NAME = 'Test Menu Section'
TEST_MENUITEM_NAME = 'Test Menu Item'
TEST_MENUITEM_DESCRIPTION = 'Test Menu Item Description'

# validation

RESTAURANT_DUPLICATE_SLUG_ERROR_STRING = \
    "This name is too similar to an existing restaurant name."
MAX_RESTAURANTS_PER_USER = 3
MAX_RESTAURANTS_PER_USER_ERROR_STRING = "You cannot register more than "\
    f"{MAX_RESTAURANTS_PER_USER} restaurants. If you wish to register a "\
    "new restaurant, you must first delete one of your existing restaurants."
RESERVED_KEYWORD_ERROR_STRING = \
    "This name is reserved and cannot be used. Please choose another name."
