#Themes and modes

## Modes

The site has been initially built in dark-mode only, but the longer-term plan is to introduce a toggle switch where the user can opt to display it in light mode. The CSS to set the mode is an html class of either `.mode-dark` or `.mode-light`.

## Themes

An editor has an option to select a theme on each page. Selecting a theme on a page will change it for that page, and all child pages, unless another selection is made further down the page tree.

There are currently 3 themes in use: coral, lagoon and banana. The CSS to set the theme is an html class of either `.theme-coral`, `.theme-lagoon` or `.theme-banana`.

## CSS Variables

All colours should be set using CSS variables, and these are updated according to the theme or mode in use on any given page.

## Defaults

The site will show in dark mode by default, and if a theme is not selected for a page or any parent pages, then it will display with the coral theme.
