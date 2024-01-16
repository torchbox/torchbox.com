from .base import *  # noqa

# #############
# General

# SECRET_KEY is required by Django to start.
SECRET_KEY = "fake_secret_key_to_run_tests"  # pragma: allowlist secret

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
