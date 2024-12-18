# Utility classes and Tailwind

Most CSS classes used in this build are designed to fit with a particular component and are designed to tie with one particular component, and not to be re-used, to make maintenance easier.

Some, such as the `listing` component are designed to be a base with variations across a number of variant components - this is made clear by the component naming: `listing--image.html`, `listing--simple.html` etc.

However, we have some utility classes which are designed for re-use, along with the option to to use Tailwind utility classes. Classes that are designed for re-use include `button`, `heading--[xyz]`, `text--[xyz]`, `link`, and `icon--listing-arrow`.

The same tailwind utility classes that are avialable in `wagtail-kit` are available in this build. `tailwind.config.js` includes the custom spacing for the build, allowing us to use classes such as `mb-spacerMini` where it wouldn't be practical to create a new scss component just for a one-off spacing adjustment.
