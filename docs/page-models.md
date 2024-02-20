# Torchbox.com - Page Models

We don't have a `BasePage` model that all page models inherit from - they inherit directly from Wagtail's `Page` model.

If creating new page models, make sure they also inherit from the following

1. the `SocialFields` mixin, so that social image and text fields are added to the 'promote' tab.
2. the `ColourThemeMixin`, so that a colour theme can be specified for the page. For more details on how the theme feature works, please see [Custom Features > Theme (docs)](custom-features/theme.md).
3. the `ContactMixin`, so that a contact can be specified for the page's footer. For more details on how the contact feature works, please see [Custom Features > Contact (docs)](custom-features/contact.md).
