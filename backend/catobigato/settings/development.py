"""Development settings — overrides base.py."""

from .base import *  # noqa

DEBUG = True
SECRET_KEY = "django...&*()"

ALLOWED_HOSTS = ["*", "localhost", "127.0.0.1"]

# CORS — allow all for development (frontend runs on port 5173)
CORS_ALLOW_ALL_ORIGINS = True

# Database — k2m where flowdesk has full access
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "k2m",
        "USER": "flowdesk",
        "PASSWORD": "FlowDesk1@3",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

# Static files
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Logging
LOGGING["loggers"]["django"]["level"] = "DEBUG"