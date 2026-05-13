"""
Django settings for CatobiGato.
Environment-aware: development, production, testing.
"""
import os
import sys

# Ensure catobigato package is importable from backend root
sys.path.insert(0, os.path.dirname(__file__))

ENV = os.getenv("DJANGO_ENV", "development")

if ENV == "production":
    from catobigato.settings.production import *  # noqa
elif ENV == "testing":
    from catobigato.settings.testing import *  # noqa
else:
    from catobigato.settings.development import *  # noqa