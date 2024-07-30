#Themes and modes

## Modes

The CSS to set the mode is an html class of either `.mode-dark` or `.mode-light`.

## Themes

An editor has an option to select a theme on each page. Selecting a theme on a page will change it for that page, and all child pages, unless another selection is made further down the page tree.

There are currently 4 themes in use: coral, lagoon, banana and earth. The CSS to set the theme is an html class of either `.theme-coral`, `.theme-lagoon`, `.theme-banana` or `.theme-earth`.

???+ note

    If you are adding a new theme, check the colour contrast for all the new accent colours added, used in the drop-caps (remember to check both dark mode and light mode). They need to pass colour contrast as if the entire drop-cap was filled with that colour.

    The drop-caps svgs use a semi-transparent version of the accent colours, and the contrast of the resulting colour also needs to be checked. The [colour contrast checker](https://chromewebstore.google.com/detail/colour-contrast-checker/nmmjeclfkgjdomacpcflgdkgpphpmnfe?hl=en-GB&utm_source=ext_sidebar) is a useful chrome extension to assist with this.

## Defaults

The site will show in dark mode by default, and if a theme is not selected for a page or any parent pages, then it will display with the coral theme.

## CSS Variables

All colours should be set using CSS variables, and these are updated according to the theme or mode in use on any given page.

The colours are named to match the figma colours. There is a section of the figma file that is only visible to editors which defines all the colours, and sets out a grid of the different colours used in different themes, which are variables file follows when setting up the themes. For reference these are in the screenshots below.

![Colour definitions](/images/colour-definitions.png)

<figcaption>Colour definitions</figcaption>

![Colour grid](/images/colour-grid.png)

<figcaption>Colour grid</figcaption>
