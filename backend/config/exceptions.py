from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            'error': True,
            'message': _flatten_errors(response.data),
            'code': response.status_code,
            'details': response.data if isinstance(response.data, dict) else {},
        }

    return response


def _flatten_errors(data):
    if isinstance(data, list):
        return str(data[0]) if data else 'An error occurred'
    if isinstance(data, dict):
        for key, val in data.items():
            if key == 'detail':
                return str(val)
            return str(val[0]) if isinstance(val, list) else str(val)
    return str(data)
