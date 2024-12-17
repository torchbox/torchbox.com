import contextlib

from .base import *  # noqa: F403


# Disable debug mode
DEBUG = False

# Error if there aren't enough proxies in between
XFF_ALWAYS_PROXY = True

with contextlib.suppress(ImportError):
    from .local import *  # noqa: F403
