from .base import *  # noqa: F403


# #############
# General

# SECRET_KEY is required by Django to start.
# pragma: allowlist nextline secret
SECRET_KEY = "fake_secret_key_to_run_tests"  # noqa: S105

# Don't redirect to HTTPS in tests.
SECURE_SSL_REDIRECT = False
# Don't send the HSTS header
SECURE_HSTS_SECONDS = 0

# Don't insist on having run birdbath
BIRDBATH_REQUIRED = False

ALLOWED_HOSTS = ["example.com", "localhost", "127.0.0.1"]

# #############
# Performance

# By default, Django uses a computationally difficult algorithm for passwords hashing.
# We don't need such a strong algorithm in tests, so use MD5
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

WAGTAILADMIN_BASE_URL = "http://localhost:8000"

# Ignore proxy count in tests
XFF_ALWAYS_PROXY = False

# Use simple static files storage in tests — no manifest required
STORAGES["staticfiles"] = {  # noqa: F405
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
}

# Use an in-memory cache for tests so they don't read from or write to the
# Redis instance shared with the dev server. Otherwise tests that exercise
# NavigationSettings.save() leave their fixture data in the real cache and
# the dev site renders a stale nav until TTL expires.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "tests-default",
    },
    "renditions": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "tests-renditions",
    },
}
