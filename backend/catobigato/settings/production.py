"""Production settings — overrides base.py."""

import os

from .base import *  # noqa

DEBUG = False

# Always read from environment in production
SECRET_KEY = os.getenv("SECRET_KEY")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "catobigato.com,www.catobigato.com").split(",")

# ─── Database ───────────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "catobigato"),
        "USER": os.getenv("DB_USER", "catobigato"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

# ─── Keycloak (KeyToMarvel.com — catobigato realm) ─────────────────
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "https://www.keytomarvel.com")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "catobigato")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "catobigato")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "")

# ─── CORS ──────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "https://catobigato.com").split(",")
    if origin.strip()
]

# ─── Security ─────────────────────────────────────────────────────
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# ─── Logging ───────────────────────────────────────────────────────
LOGGING["loggers"]["django"]["level"] = "WARNING"