"""
CatobiGato settings package.
Provides environment-aware settings: development / production / testing.
Default: development. Override with DJANGO_ENV env var.
"""
import os

ENV = os.getenv("DJANGO_ENV", "development")
__all__ = ["base", "development", "production", "testing"]

# Import base settings first (always needed)
from .base import *  # noqa

# Import environment-specific overrides
if ENV == "production":
    from . import production as _env_settings
    from .production import *  # noqa
elif ENV == "testing":
    from . import testing as _env_settings
    from .testing import *  # noqa
else:
    from . import development as _env_settings
    from .development import *  # noqa