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

# Give tests their own in-memory cache.
#
# `base.py` uses Redis whenever REDIS_URL is set, which is the case inside the dev
# container — so tests would otherwise share a cache with the running dev site. That
# leaks state across databases: Wagtail caches site root paths under a fixed key and
# only invalidates it when a Site is saved, so a stale entry written against the dev
# database makes `page.url` resolve to None in tests, and cached values survive between
# test runs. Locmem is per-process, which also matches how CI behaves (no REDIS_URL).
CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    "renditions": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
}

WAGTAILADMIN_BASE_URL = "http://localhost:8000"

# Ignore proxy count in tests
XFF_ALWAYS_PROXY = False

# Use simple static files storage in tests — no manifest required
STORAGES["staticfiles"] = {  # noqa: F405
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
}
