# jobs/context_processors.py
from emails.views import get_unread_emails

def unread_email_count(request):
    try:
        email_subjects, _ = get_unread_emails(request.user)  # If needed
        unread_email_count = len(email_subjects) if email_subjects else 0
        return {
            'unread_email_count': unread_email_count,
        }
    except Exception as e:
        logger.error(f"Error in unread_email_count context processor: {e}")
        return {
            'unread_email_count': 0,
        }

