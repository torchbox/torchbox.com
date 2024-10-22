from .base import *  # noqa

# Disable debug mode
DEBUG = False

# Error if there aren't enough proxies in between
XFF_ALWAYS_PROXY = True

try:
    from .local import *  # noqa
except ImportError:
    pass
