from oauth.views import get_unread_emails

def unread_email_count(request):
    email_subjects, _ = get_unread_emails()
    unread_count = len(email_subjects) if email_subjects else 0
    print("Context Processor: Unread Email Count =", unread_count)  # Debug print
    return {
        'unread_email_count': unread_count
    }

