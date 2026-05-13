"""Django settings for CatobiGato — delegates to catobigato.settings package."""
import os

ENV = os.getenv("DJANGO_ENV", "development")

# Import the settings package (contains __init__.py that chooses env-specific settings)
if ENV == "production":
    from catobigato.settings.production import *  # noqa
elif ENV == "testing":
    from catobigato.settings.testing import *  # noqa
else:
    from catobigato.settings.development import *  # noqa