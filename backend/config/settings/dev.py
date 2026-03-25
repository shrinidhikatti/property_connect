from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# PostgreSQL (local dev — no PostGIS yet, plain postgres for Phase 1)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='propconnect'),
        'USER': config('DB_USER', default='propconnect'),
        'PASSWORD': config('DB_PASSWORD', default='propconnect'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# CORS — allow Vite dev server
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5656',
    'http://127.0.0.1:5656',
]
CORS_ALLOW_CREDENTIALS = True

# Redis cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
    }
}

# Email — console backend in dev
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable throttling in dev for easier testing
REST_FRAMEWORK_THROTTLE_RATES_OVERRIDE = False
