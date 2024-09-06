from oauth.views import get_unread_emails
import logging
import json

logger = logging.getLogger(__name__)

def unread_email_count(request):
    try:
        # Ensure you are passing the correct argument to get_unread_emails()
        email_subjects, _ = get_unread_emails(request.user)
        unread_count = len(email_subjects) if isinstance(email_subjects, list) else 0
        logger.debug(f"Context Processor: Unread Email Count = {unread_count}")
    except Exception as e:
        logger.error(f"Error in unread_email_count context processor: {e}", exc_info=True)
        unread_count = 0

    return {
        'unread_email_count': unread_count
    }

