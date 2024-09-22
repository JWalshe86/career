import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'career.settings')  # Change to your project settings
django.setup()

# Now import your modules
import logging
from emails.utils import get_user, load_credentials, get_unread_emails

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def test_user_and_credentials(username):
    user = get_user(username)
    if user:
        creds = load_credentials(user)
        if creds:
            print(f"Loaded credentials for user '{username}':")
            print(f"Access Token: {creds.token}")
            print(f"Refresh Token: {creds.refresh_token}")
            print(f"Token Expiry: {creds.expiry}")

            # Fetch unread emails
            unread_emails, error = get_unread_emails(creds)
            if error:
                print(f"Error fetching unread emails: {error}")
            else:
                print("Unread Emails:", unread_emails)
        else:
            print(f"No credentials found for user '{username}'")
    else:
        print(f"User '{username}' not found")

if __name__ == "__main__":
    test_user_and_credentials('johnwalshe')  # Change the username as needed

