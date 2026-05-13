# Testing settings — overrides base.py

from .base import *  # noqa

DEBUG = True

SECRET_KEY = "django-insecure-test-only"

ALLOWED_HOSTS = ["*"]

# Test database (in-memory SQLite for speed)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Disable migrations in tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Faster password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# No CORS restrictions in tests
CORS_ALLOWED_ORIGINS = ["*"]

# Logging - silent in tests
LOGGING["loggers"]["django"]["level"] = "ERROR"