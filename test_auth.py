import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'career.settings')  # Adjust this to your settings module
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

def test_authentication(username, password):
    user = authenticate(username=username, password=password)
    if user is not None:
        print("Authentication successful!")
    else:
        print("Authentication failed.")

if __name__ == "__main__":
    # Set your username and password here
    test_username = 'johnwalshe2'  # Change to your username
    test_password = 'Sunshine7!'     # Change to your password

    test_authentication(test_username, test_password)

