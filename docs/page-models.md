# Torchbox.com - Page Models

We don't have a `BasePage` model that all page models inherit from - they inherit directly from Wagtail's `Page` model.

If creating new page models, make sure they also inherit from the `SocialFields` mixin, so that social image and text fields are added to the 'promote' tab.
