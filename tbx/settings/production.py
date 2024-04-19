from .base import *  # noqa

# Disable debug mode
DEBUG = False


try:
    from .local import *  # noqa
except ImportError:
    pass
