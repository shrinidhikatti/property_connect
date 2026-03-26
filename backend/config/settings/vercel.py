"""
Settings for Vercel deployment.
- Standard PostgreSQL (no PostGIS — GDAL not available on Vercel)
- WhiteNoise for static files
- Redis optional (falls back to in-memory cache)
- No Celery / Daphne (serverless — no background workers or WebSocket)
"""
from .base import *
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = ['*']  # Vercel assigns random subdomains; lock down after custom domain

# ── Database (Neon / Vercel Postgres free tier) ───────────────────────────────
# Set DATABASE_URL in Vercel environment variables
DATABASES = {
    'default': dj_database_url.config(
        env='DATABASE_URL',
        conn_max_age=600,
        ssl_require=True,
    )
}

# ── Static files via WhiteNoise ───────────────────────────────────────────────
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_AUTOREFRESH = True  # serve without collectstatic

# ── CORS — allow everything during testing ────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# ── Cache: Redis (Upstash) if set, else in-memory ────────────────────────────
_REDIS = config('REDIS_URL', default='')
if _REDIS:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': _REDIS,
        }
    }
else:
    CACHES = {
        'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}
    }

# ── Channels: in-memory (WebSocket not supported on Vercel) ──────────────────
CHANNEL_LAYERS = {
    'default': {'BACKEND': 'channels.layers.InMemoryChannelLayer'}
}

# ── No SSL redirect (Vercel terminates TLS) ───────────────────────────────────
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
