import sys
import os
import json
import traceback

# Resolve backend path relative to this file's location
_HERE = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.join(_HERE, '..', 'backend')
sys.path.insert(0, os.path.normpath(_BACKEND))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.vercel')

try:
    from django.core.wsgi import get_wsgi_application
    _django_app = get_wsgi_application()
    _startup_error = None
except Exception:
    _django_app = None
    _startup_error = traceback.format_exc()


def app(environ, start_response):
    # Bare-metal health check — no Django involved
    if environ.get('PATH_INFO', '') == '/api/health':
        body = json.dumps({
            'ok': _startup_error is None,
            'python': sys.version,
            'backend_path': _BACKEND,
            'startup_error': _startup_error,
        }, indent=2).encode()
        start_response('200 OK', [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(body))),
        ])
        return [body]

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
