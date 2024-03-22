# Hotjar tracking in Wagtail admin

In order to aid design decisions for the Wagtail core team, we have Hotjar tracking enabled in the admin area of the torchbox.com site. This is with permission of the main editors, Lily and Lisa, and has also been active whilst some editors who are new to wagtail have worked on the site - with their permission too.

The tracking is enabled in `core/wagtail_hooks.py` and can be removed at any time by deleting the `ADMIN_HOTJAR_SITE_ID` environment variable.
