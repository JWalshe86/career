import os
from django.core.wsgi import get_wsgi_application

print("Starting WSGI application...")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'career.settings')
print("DJANGO_SETTINGS_MODULE set to:", os.getenv('DJANGO_SETTINGS_MODULE'))
application = get_wsgi_application()

