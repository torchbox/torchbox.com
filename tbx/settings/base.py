# Django settings for tbx project.
import contextlib

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys

import dj_database_url


# Configuration from environment variables
env = os.environ.copy()

# On Torchbox servers, many environment variables are prefixed with "CFG_"
for key, value in os.environ.items():
    if key.startswith("CFG_"):
        env[key[4:]] = value

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

# Basic settings
DEBUG = False

APP_NAME = env.get("APP_NAME", "torchbox")

if "SECRET_KEY" in env:
    SECRET_KEY = env["SECRET_KEY"]

if "ALLOWED_HOSTS" in env:
    ALLOWED_HOSTS = env["ALLOWED_HOSTS"].split(",")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/


# Application definition

INSTALLED_APPS = [
    "scout_apm.django",
    "tbx.blog",
    "tbx.core.apps.TorchboxCoreAppConfig",
    "tbx.divisions",
    "tbx.events",
    "tbx.impact_reports",
    "tbx.navigation",
    "tbx.people",
    "tbx.taxonomy",
    "tbx.work",
    "tbx.images",
    "tbx.users",
    "tbx.services",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "wagtailmarkdown",
    "modelcluster",
    "taggit",
    "phonenumber_field",
    "django.contrib.humanize",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "wagtail.contrib.settings",
    "pattern_library",
    "tbx.project_styleguide.apps.ProjectStyleguideConfig",
    "wagtailaccessibility",
    "wagtail_purge",
    "birdbath",
    "wagtailmedia",
    "wagtail.contrib.typed_table_block",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django_permissions_policy.PermissionsPolicyMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "xff.middleware.XForwardedForMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # Clickjacking prevention. Default: X_FRAME_OPTIONS = 'DENY'
    # See https://docs.djangoproject.com/en/dev/ref/clickjacking/#preventing-clickjacking
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF = "tbx.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(PROJECT_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "tbx.core.context_processors.global_vars",
                "wagtail.contrib.settings.context_processors.settings",
            ],
            "builtins": ["pattern_library.loader_tags"],
        },
    },
]

WSGI_APPLICATION = "tbx.wsgi.application"

# As of Django 3.2, the type of the primary key auto field needs to be defined
# either gloablly or in each AppConfig.
# See also: https://docs.djangoproject.com/en/3.2/releases/3.2/#customizing-type-of-auto-created-primary-keys
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Database
# https://docs.djangoproject.com/en/stable/ref/settings/#databases
# https://github.com/kennethreitz/dj-database-url

DATABASES = {
    "default": dj_database_url.config(
        conn_max_age=600, default=f"postgres:///{APP_NAME}"
    )
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/
LANGUAGE_CODE = "en-gb"

TIME_ZONE = "Europe/London"

USE_I18N = True


USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATICFILES_DIRS = [os.path.join(PROJECT_DIR, "static_compiled")]

STATIC_ROOT = env.get("STATIC_DIR", os.path.join(BASE_DIR, "static"))
STATIC_URL = env.get("STATIC_URL", "/static/")

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

# Place static files that need a specific URL (such as robots.txt and favicon.ico) in the "public" folder
WHITENOISE_ROOT = os.path.join(BASE_DIR, "public")

# Media files

MEDIA_ROOT = env.get("MEDIA_DIR", os.path.join(BASE_DIR, "media"))
MEDIA_URL = env.get("MEDIA_URL", "/media/")
MEDIA_PREFIX = env.get("MEDIA_PREFIX", "")


# Server-side cache settings. Do not confuse with front-end cache.
# https://docs.djangoproject.com/en/stable/topics/cache/
# If the server has a Redis instance exposed via a URL string in the REDIS_URL
# environment variable, prefer that. Otherwise, use the database backend. We
# usually use Redis in production and database backend on staging and dev. In
# order to use database cache backend you need to run
# "django-admin createcachetable" to create a table for the cache.
#
# Do not use the same Redis instance for other things like Celery!

# Prefer the TLS connection URL over non
REDIS_URL = env.get("REDIS_TLS_URL", env.get("REDIS_URL"))

if REDIS_URL:
    connection_pool_kwargs = {}

    if REDIS_URL.startswith("rediss"):
        # Heroku Redis uses self-signed certificates for secure redis conections. https://stackoverflow.com/a/66286068
        # When using TLS, we need to disable certificate validation checks.
        connection_pool_kwargs["ssl_cert_reqs"] = None

    redis_options = {
        "IGNORE_EXCEPTIONS": True,
        "SOCKET_CONNECT_TIMEOUT": 2,  # seconds
        "SOCKET_TIMEOUT": 2,  # seconds
        "CONNECTION_POOL_KWARGS": connection_pool_kwargs,
    }

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL + "/0",
            "OPTIONS": redis_options,
        },
        "renditions": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL + "/1",
            "OPTIONS": redis_options,
        },
    }
    DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": "database_cache",
        }
    }


# Search
# https://docs.wagtail.io/en/latest/topics/search/backends.html

WAGTAILSEARCH_BACKENDS = {
    "default": {"BACKEND": "wagtail.search.backends.database"},
}


# S3 configuration
if "AWS_STORAGE_BUCKET_NAME" in env:
    STORAGES["default"]["BACKEND"] = "storages.backends.s3.S3Storage"

    AWS_STORAGE_BUCKET_NAME = env["AWS_STORAGE_BUCKET_NAME"]
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_FILE_OVERWRITE = False
    AWS_S3_MAX_MEMORY_SIZE = 2 * 1024 * 1024  # 2MB

    # You need this to enable signing files. Some old regions may have use a
    # different version than v4.
    AWS_S3_SIGNATURE_VERSION = env.get("AWS_S3_SIGNATURE_VERSION", "s3v4")

    # Set individual files to be private and only allow access to them via
    # bucket policy.
    AWS_DEFAULT_ACL = "private"

    if "AWS_S3_SECURE_URLS" in env:
        AWS_S3_SECURE_URLS = env["AWS_S3_SECURE_URLS"].strip().lower() == "true"

    if "AWS_S3_ENDPOINT_URL" in env:
        # This setting is required for signing.
        # Please use endpoint from
        # https://docs.aws.amazon.com/general/latest/gr/rande.html#s3_region
        # e.g. "https://s3.eu-west-2.amazonaws.com"
        AWS_S3_ENDPOINT_URL = env["AWS_S3_ENDPOINT_URL"]

    if "AWS_S3_REGION_NAME" in env:
        # This setting is required for signing.
        AWS_S3_REGION_NAME = env["AWS_S3_REGION_NAME"]

    if "AWS_S3_CUSTOM_DOMAIN" in env:
        AWS_S3_CUSTOM_DOMAIN = env["AWS_S3_CUSTOM_DOMAIN"]

    INSTALLED_APPS += ("storages",)


# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        # Send logs with at least INFO level to the console.
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s][%(process)d][%(levelname)s][%(name)s] %(message)s"
        }
    },
    "loggers": {
        "tbx": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "wagtail": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "xff": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}


# Email settings
if "EMAIL_HOST" in env:
    EMAIL_HOST = env["EMAIL_HOST"]

if "EMAIL_PORT" in env:
    with contextlib.suppress(ValueError):
        EMAIL_PORT = int(env["EMAIL_PORT"])

if "EMAIL_HOST_USER" in env:
    EMAIL_HOST_USER = env["EMAIL_HOST_USER"]

if "EMAIL_HOST_PASSWORD" in env:
    EMAIL_HOST_PASSWORD = env["EMAIL_HOST_PASSWORD"]

if env.get("EMAIL_USE_TLS", "false").lower().strip() == "true":
    EMAIL_USE_TLS = True

if env.get("EMAIL_USE_SSL", "false").lower().strip() == "true":
    EMAIL_USE_SSL = True

if "EMAIL_SUBJECT_PREFIX" in env:
    EMAIL_SUBJECT_PREFIX = env["EMAIL_SUBJECT_PREFIX"]

if "SERVER_EMAIL" in env:
    SERVER_EMAIL = DEFAULT_FROM_EMAIL = env["SERVER_EMAIL"]


# Sentry configuration.
# See instructions on the intranet:
# https://intranet.torchbox.com/delivering-projects/tech/starting-new-project/#sentry
is_in_shell = len(sys.argv) > 1 and sys.argv[1] in ["shell", "shell_plus"]

if "SENTRY_DSN" in env and not is_in_shell:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.utils import get_default_release

    sentry_kwargs = {
        "dsn": env["SENTRY_DSN"],
        "integrations": [DjangoIntegration()],
    }

    # There's a chooser to toggle between environments at the top right corner on sentry.io
    # Values are typically 'staging' or 'production' but can be set to anything else if needed.
    # `heroku config:set SENTRY_ENVIRONMENT=production`
    if sentry_environment := env.get("SENTRY_ENVIRONMENT"):
        sentry_kwargs.update({"environment": sentry_environment})

    release = get_default_release()
    if release is None:
        # Assume this is a Heroku-hosted app with the "runtime-dyno-metadata" lab enabled.
        # see https://devcenter.heroku.com/articles/dyno-metadata
        # `heroku labs:enable runtime-dyno-metadata`
        release = env.get("HEROKU_RELEASE_VERSION", None)

    sentry_kwargs.update({"release": release})
    sentry_sdk.init(**sentry_kwargs)


# Security configuration
# https://docs.djangoproject.com/en/stable/ref/middleware/#module-django.middleware.security

# Force HTTPS redirect (enabled by default!)
# https://docs.djangoproject.com/en/stable/ref/settings/#secure-ssl-redirect
SECURE_SSL_REDIRECT = True

# This will allow the cache to swallow the fact that the website is behind TLS
# and inform the Django using "X-Forwarded-Proto" HTTP header.
# https://docs.djangoproject.com/en/stable/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# This is a setting activating the HSTS header. This will enforce the visitors to use
# HTTPS for an amount of time specified in the header. Since we are expecting our apps
# to run via TLS by default, this header is activated by default.
# The header can be deactivated by setting this setting to 0, as it is done in the
# dev and testing settings.
# https://docs.djangoproject.com/en/stable/ref/settings/#secure-hsts-seconds
DEFAULT_HSTS_SECONDS = 30 * 24 * 60 * 60  # 30 days
SECURE_HSTS_SECONDS = DEFAULT_HSTS_SECONDS
if "SECURE_HSTS_SECONDS" in env:
    with contextlib.suppress(ValueError):
        SECURE_HSTS_SECONDS = int(env["SECURE_HSTS_SECONDS"])

# We don't enforce HSTS on subdomains as anything at subdomains is likely outside our control.
# https://docs.djangoproject.com/en/3.2/ref/settings/#secure-hsts-include-subdomains
SECURE_HSTS_INCLUDE_SUBDOMAINS = False

# https://docs.djangoproject.com/en/stable/ref/settings/#secure-browser-xss-filter
SECURE_BROWSER_XSS_FILTER = True

# https://docs.djangoproject.com/en/stable/ref/settings/#secure-content-type-nosniff
SECURE_CONTENT_TYPE_NOSNIFF = True

# https://docs.djangoproject.com/en/stable/ref/middleware/#referrer-policy
SECURE_REFERRER_POLICY = env.get(
    "SECURE_REFERRER_POLICY", "no-referrer-when-downgrade"
).strip()

# Content Security policy settings
# http://django-csp.readthedocs.io/en/latest/configuration.html
if "CSP_DEFAULT_SRC" in env:
    MIDDLEWARE.append("csp.middleware.CSPMiddleware")

    # The “special” source values of 'self', 'unsafe-inline', 'unsafe-eval', and 'none' must be quoted!
    # e.g.: CSP_DEFAULT_SRC = "'self'" Without quotes they will not work as intended.

    CSP_DEFAULT_SRC = env["CSP_DEFAULT_SRC"].split(",")
    if "CSP_SCRIPT_SRC" in env:
        CSP_SCRIPT_SRC = env["CSP_SCRIPT_SRC"].split(",")
    if "CSP_STYLE_SRC" in env:
        CSP_STYLE_SRC = env["CSP_STYLE_SRC"].split(",")
    if "CSP_IMG_SRC" in env:
        CSP_IMG_SRC = env["CSP_IMG_SRC"].split(",")
    if "CSP_CONNECT_SRC" in env:
        CSP_CONNECT_SRC = env["CSP_CONNECT_SRC"].split(",")
    if "CSP_FONT_SRC" in env:
        CSP_FONT_SRC = env["CSP_FONT_SRC"].split(",")
    if "CSP_BASE_URI" in env:
        CSP_BASE_URI = env["CSP_BASE_URI"].split(",")
    if "CSP_OBJECT_SRC" in env:
        CSP_OBJECT_SRC = env["CSP_OBJECT_SRC"].split(",")

# Permissions policy settings
# Uses django-permissions-policy to return the header.
# https://github.com/adamchainz/django-permissions-policy
# The list of Chrome-supported features are in:
# https://github.com/w3c/webappsec-permissions-policy/blob/main/features.md
PERMISSIONS_POLICY = {
    "accelerometer": [],
    "ambient-light-sensor": [],
    "autoplay": ["self", "https://www.youtube-nocookie.com"],
    "camera": [],
    "display-capture": [],
    "document-domain": [],
    "encrypted-media": [],
    "geolocation": [],
    "gyroscope": [],
    "magnetometer": [],
    "microphone": [],
    "midi": [],
    "payment": [],
    "picture-in-picture": [],
    "usb": [],
}

# Wagtail settings
WAGTAIL_SITE_NAME = "Torchbox"

if "PRIMARY_HOST" in env:
    WAGTAILADMIN_BASE_URL = "https://{}".format(env["PRIMARY_HOST"])


# Override the Image class used by wagtailimages with a custom one
WAGTAILIMAGES_IMAGE_MODEL = "images.CustomImage"

pixel_limit = env.get("WAGTAILIMAGES_MAX_IMAGE_PIXELS")
WAGTAILIMAGES_MAX_IMAGE_PIXELS = int(pixel_limit) if pixel_limit else 10_000_000

max_upload_size = env.get("WAGTAILIMAGES_MAX_UPLOAD_SIZE")
WAGTAILIMAGES_MAX_UPLOAD_SIZE = (
    int(max_upload_size) if max_upload_size else 2 * 1024 * 1024
)  # 2MB

# The Django default for the maximum number of GET or POST parameters is 1000. For
# especially large Wagtail pages with many fields, we need to override this. See
# https://docs.djangoproject.com/en/3.2/ref/settings/#data-upload-max-number-fields
DATA_UPLOAD_MAX_NUMBER_FIELDS = int(env.get("DATA_UPLOAD_MAX_NUMBER_FIELDS", 10_000))

# Basic auth settings
if env.get("BASIC_AUTH_ENABLED", "false").lower().strip() == "true":
    MIDDLEWARE.insert(0, "baipw.middleware.BasicAuthIPWhitelistMiddleware")
    BASIC_AUTH_LOGIN = env.get("BASIC_AUTH_LOGIN")
    BASIC_AUTH_PASSWORD = env.get("BASIC_AUTH_PASSWORD")

    # Wagtail requires Authorization header to be present for the previews
    BASIC_AUTH_DISABLE_CONSUMING_AUTHORIZATION_HEADER = True

    BASIC_AUTH_WHITELISTED_IP_NETWORKS = [
        # Torchbox networks.
        "78.32.251.192/28",
        "89.197.53.244/30",
        "193.227.244.0/23",
        "2001:41c8:103::/48",
    ]
    if "BASIC_AUTH_WHITELISTED_HTTP_HOSTS" in env:
        BASIC_AUTH_WHITELISTED_HTTP_HOSTS = env[
            "BASIC_AUTH_WHITELISTED_HTTP_HOSTS"
        ].split(",")

XFF_TRUSTED_PROXY_DEPTH = int(env.get("XFF_TRUSTED_PROXY_DEPTH", 1))

AUTH_USER_MODEL = "users.User"

# Front-end cache
# https://docs.wagtail.io/en/latest/reference/contrib/frontendcache.html

if "FRONTEND_CACHE_PURGE_URL" in env:
    INSTALLED_APPS.append("wagtail.contrib.frontend_cache")
    WAGTAILFRONTENDCACHE = {
        "default": {
            "BACKEND": "wagtail.contrib.frontend_cache.backends.HTTPBackend",
            "LOCATION": env["FRONTEND_CACHE_PURGE_URL"],
        },
    }
elif "FRONTEND_CACHE_CLOUDFLARE_TOKEN" in env:
    INSTALLED_APPS.append("wagtail.contrib.frontend_cache")
    WAGTAILFRONTENDCACHE = {
        "default": {
            "BACKEND": "wagtail.contrib.frontend_cache.backends.CloudflareBackend",
            "BEARER_TOKEN": env["FRONTEND_CACHE_CLOUDFLARE_TOKEN"],
            "ZONEID": env["FRONTEND_CACHE_CLOUDFLARE_ZONEID"],
        },
    }


# Set s-max-age header that is used by reverse proxy/front end cache. See
# urls.py
with contextlib.suppress(ValueError):
    CACHE_CONTROL_S_MAXAGE = int(env.get("CACHE_CONTROL_S_MAXAGE", 600))


# Give front-end cache 30 second to revalidate the cache to avoid hitting the
# backend. See urls.py
CACHE_CONTROL_STALE_WHILE_REVALIDATE = int(
    env.get("CACHE_CONTROL_STALE_WHILE_REVALIDATE", 30)
)

# Embeds
WAGTAILEMBEDS_FINDERS = [
    # https://github.com/RealOrangeOne/wagtail-lite-youtube-embed
    {"class": "lite_youtube_embed.LiteYouTubeEmbedFinder"},
    # Handles all other oEmbed providers the default way
    {"class": "wagtail.embeds.finders.oembed"},
]
INSTAGRAM_OEMBED_APP_ID = env.get("INSTAGRAM_OEMBED_APP_ID")
INSTAGRAM_OEMBED_APP_SECRET = env.get("INSTAGRAM_OEMBED_APP_SECRET")
if INSTAGRAM_OEMBED_APP_ID and INSTAGRAM_OEMBED_APP_SECRET:
    WAGTAILEMBEDS_FINDERS.insert(
        0,
        {
            "class": "wagtail.embeds.finders.instagram",
            "app_id": INSTAGRAM_OEMBED_APP_ID,
            "app_secret": INSTAGRAM_OEMBED_APP_SECRET,
        },
    )

# Embledly
if "EMBEDLY_KEY" in env:
    EMBEDLY_KEY = env["EMBEDLY_KEY"]


# Newsletter

if "MAILCHIMP_KEY" in env:
    MAILCHIMP_KEY = env["MAILCHIMP_KEY"]

if "MAILCHIMP_MAILING_LIST_ID" in env:
    MAILCHIMP_MAILING_LIST_ID = env["MAILCHIMP_MAILING_LIST_ID"]


WAGTAIL_PASSWORD_REQUIRED_TEMPLATE = (
    # pragma: allowlist nextline secret
    "patterns/pages/wagtail/password_required.html"  # noqa: S105
)
# Styleguide
PATTERN_LIBRARY_ENABLED = env.get("PATTERN_LIBRARY_ENABLED", "false").lower() == "true"
PATTERN_LIBRARY = {
    "SECTIONS": (
        ("styleguide", ["patterns/styleguide"]),
        ("atoms", ["patterns/atoms"]),
        ("molecules", ["patterns/molecules"]),
        ("organisms", ["patterns/organisms"]),
        ("pages", ["patterns/pages"]),
        ("navigation", ["patterns/navigation"]),
    ),
    "TEMPLATE_SUFFIX": ".html",
    "PATTERN_BASE_TEMPLATE_NAME": "patterns/base.html",
    "BASE_TEMPLATE_NAMES": ["patterns/base_page.html"],
}


# Google Tag Manager ID from env
GOOGLE_TAG_MANAGER_ID = env.get("GOOGLE_TAG_MANAGER_ID")

# Trial Hotjar tracking for the CMS admin.
ADMIN_HOTJAR_SITE_ID = env.get("ADMIN_HOTJAR_SITE_ID")

# Allows us to toggle search indexing via an environment variable.
SEO_NOINDEX = env.get("SEO_NOINDEX", "false").lower() == "true"


# Birdbath - Database anonymisation
# -----------------------------------------------------------------------------
# Configure django-birdbath to anonymise data when syncing database
BIRDBATH_USER_ANONYMISER_EXCLUDE_SUPERUSERS = True
BIRDBATH_USER_ANONYMISER_EXCLUDE_EMAIL_RE = r"(torchbox\.com)$"
# Do not anonymise data on any heroku app containing 'production' in app name
BIRDBATH_CHECKS = ["birdbath.checks.contrib.heroku.HerokuNotProductionCheck"]
BIRDBATH_REQUIRED = env.get("BIRDBATH_REQUIRED", "true").lower() == "true"
# Add project specific processors here to anonymise or delete sensitive data.
# See https://git.torchbox.com/internal/django-birdbath/#processors
BIRDBATH_PROCESSORS = [
    "birdbath.processors.users.UserEmailAnonymiser",
    "birdbath.processors.users.UserPasswordAnonymiser",
]

WILLOW_OPTIMIZERS = True


# Rich text settings
DEFAULT_RICH_TEXT_FEATURES = [
    "h2",
    "h3",
    "h4",
    "bold",
    "italic",
    "ul",
    "ol",
    "link",
    "document-link",
]
NO_HEADING_RICH_TEXT_FEATURES = ["bold", "italic", "ul", "ol", "link", "document-link"]
PARAGRAPH_RICH_TEXT_FEATURES = ["bold", "italic", "link", "document-link"]
WAGTAILADMIN_RICH_TEXT_EDITORS = {
    "default": {
        "WIDGET": "wagtail.admin.rich_text.DraftailRichTextArea",
        "OPTIONS": {
            "features": DEFAULT_RICH_TEXT_FEATURES,
        },
    },
}

# Used when switching between light and dark modes
ALLOWED_MODES = ["light", "dark"]
BASE_DOMAIN = env.get(
    "BASE_DOMAIN", ""
)  # this is used for sharing cookies across subdomains
