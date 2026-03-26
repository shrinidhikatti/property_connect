import sys
import os
import json
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.vercel')

try:
    from django.core.wsgi import get_wsgi_application
    _django_app = get_wsgi_application()
    _startup_error = None
except Exception:
    _django_app = None
    _startup_error = traceback.format_exc()


def app(environ, start_response):
    if _startup_error:
        body = json.dumps({
            'error': 'Django failed to start',
            'detail': _startup_error,
        }).encode()
        start_response('500 Internal Server Error', [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(body))),
        ])
        return [body]
    return _django_app(environ, start_response)
