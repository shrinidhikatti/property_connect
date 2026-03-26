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

    # One-time: seed test users into Neon DB
    if path == '/api/seed-users':
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            users_data = [
                {'username': 'superadmin', 'email': 'admin@propconnect.in',
                 'password': 'Admin@1234', 'first_name': 'Super', 'last_name': 'Admin',
                 'phone': '9000000001', 'role': 'seller', 'is_staff': True,
                 'is_superuser': True, 'is_phone_verified': True},
                {'username': 'seller_ravi', 'email': 'ravi.seller@propconnect.in',
                 'password': 'Seller@1234', 'first_name': 'Ravi', 'last_name': 'Kulkarni',
                 'phone': '9000000002', 'role': 'seller', 'is_phone_verified': True},
                {'username': 'advocate_priya', 'email': 'priya.advocate@propconnect.in',
                 'password': 'Advocate@1234', 'first_name': 'Priya', 'last_name': 'Desai',
                 'phone': '9000000003', 'role': 'advocate', 'is_phone_verified': True},
                {'username': 'buyer_amit', 'email': 'amit.buyer@propconnect.in',
                 'password': 'Buyer@1234', 'first_name': 'Amit', 'last_name': 'Patil',
                 'phone': '9000000004', 'role': 'buyer', 'is_phone_verified': True},
            ]
            created = []
            for ud in users_data:
                pw = ud.pop('password')
                if User.objects.filter(username=ud['username']).exists():
                    created.append(f"SKIP {ud['username']}")
                    continue
                u = User(**ud)
                u.set_password(pw)
                u.save()
                created.append(f"OK {ud['username']}")
            return _json_response(start_response, '200 OK', {'users': created})
        except Exception:
            return _json_response(start_response, '500 Internal Server Error', {
                'detail': traceback.format_exc()
            })

    # Fix user emails to match seed data
    if path == '/api/fix-emails':
        try:
            from django.db import connection
            fixes = [
                ("superadmin", "admin@propconnect.in"),
                ("seller_ravi", "ravi.seller@propconnect.in"),
                ("advocate_priya", "priya.advocate@propconnect.in"),
                ("buyer_amit", "amit.buyer@propconnect.in"),
            ]
            results = []
            with connection.cursor() as cursor:
                for uname, email in fixes:
                    cursor.execute(
                        "UPDATE users SET email = %s WHERE username = %s",
                        [email, uname]
                    )
                    results.append(f"{uname} -> {email} ({cursor.rowcount})")
            return _json_response(start_response, '200 OK', {'results': results})
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
