"""
Vercel Python serverless entry point.
Routes all /api/v1/* requests to the Django WSGI app.
"""
import sys
import os

# Add backend/ to the Python path so Django can find its modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.vercel')

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
