# jobs/context_processors.py
from emails.views import get_unread_emails

# jobs/context_processors.py
# No longer import get_unread_emails
def unread_email_count(request):
    return {
        'unread_email_count': 0,  # Default to 0 if needed
    }

