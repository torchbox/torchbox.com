# Light and dark mode

The approach we use closely follows that used on the RNIB site.

## Dark mode by default

For sustainability reasons, we have a 'dark-mode-first' approach and serve up the site in dark mode by default.

This means that we do not check the user's preference using `prefers-color-scheme`, because there is no way to distinguish between 'light' and setting no preference - see https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme#syntax. If we could detect a specific preference for light mode we could serve light mode up to those users - but if we serve it to users who have not set a preference as well then we are no longer serving dark mode by default.

## torchbox-mode cookie

The user can switch to light mode, and their preference will be saved in a `torchbox-mode` cookie. This always has a value of either `light` or `dark` - if it is set to anything different the site will be served in dark mode. If it is not present the site will be served in dark mode.

The cookie is set via JavaScript when the user clicks the toggle in the header area of the site. If JavaScript is disabled for any reason, the toggle submits a form, which will set the cookie on the server side, and refresh the page with the new mode enabled.

The cookie is always read on the server-side, which allows us to avoid a FOUC that might happen with reading the cookie with JavaScript. The page will be served up with a class of `mode-light` or `mode-dark` on the html class depending on the value of the cookie.

## Styling

See [themes and modes](/front-end/themes_and_modes).

## Incident form

The incident form is embedded in an iframe at https://torchbox.com/incident/. It also reads the `torchbox-mode` cookie and will render in dark or light mode accordingly - it also has some JavaScript that will watch for the cookie change and dynamically update the theme if it is switched whilst the incident form page is being viewed.

The `torchbox-mode` cookie therefore explicitly sets a `domain` value in order to be read by `incident-form.torchbox.com` where the form is hosted.

Note that there isn't any easy way to test the incident form's reading of the `torchbox-mode` cookie locally, as the domains won't match.

## Cloudflare workers

In order to avoid cloudflare caching an incorrect version of a page, we use some custom cloudflare workers to ensure that both versions of the page are cached, and the user's preference respected.
