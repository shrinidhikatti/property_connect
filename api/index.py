import sys
import os
import json
import traceback

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


def _json_response(start_response, status, data):
    body = json.dumps(data, indent=2).encode()
    start_response(status, [
        ('Content-Type', 'application/json'),
        ('Content-Length', str(len(body))),
    ])
    return [body]


def app(environ, start_response):
    path = environ.get('PATH_INFO', '')

    # Health check — no Django involved
    if path == '/api/health':
        return _json_response(start_response, '200 OK', {
            'ok': _startup_error is None,
            'python': sys.version,
            'startup_error': _startup_error,
        })

    # DB connectivity test
    if path == '/api/test-db':
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            return _json_response(start_response, '200 OK', {'db': 'ok'})
        except Exception:
            return _json_response(start_response, '500 Internal Server Error', {
                'db': 'error', 'detail': traceback.format_exc()
            })

    # One-time fix: approve all draft properties so public listing works
    if path == '/api/approve-properties':
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("UPDATE properties SET status = 'approved' WHERE status = 'draft'")
                count = cursor.rowcount
            return _json_response(start_response, '200 OK', {'updated': count})
        except Exception:
            return _json_response(start_response, '500 Internal Server Error', {
                'detail': traceback.format_exc()
            })

    if _startup_error:
        return _json_response(start_response, '500 Internal Server Error', {
            'error': 'Django failed to start',
            'detail': _startup_error,
        })

    # Wrap every Django request so errors show as JSON instead of blank 500
    try:
        return _django_app(environ, start_response)
    except Exception:
        return _json_response(start_response, '500 Internal Server Error', {
            'error': 'Unhandled exception',
            'detail': traceback.format_exc(),
        })
