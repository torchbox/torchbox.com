# Page theme

The Theme feature enables the customization of page styles through the application of color themes. It allows content editors to define a theme for individual pages, which cascades down to all descendant pages. If no specific theme is selected for a page, it inherits the theme from its ancestors, defaulting to whatever is the deafult theme as defined in the projects's stylesheets.

## Theme Options

The available color themes are defined using the `tbx.core.utils.models.ColourTheme` enumeration. Each theme option consists of a CSS class name and a human-readable label. The following themes are available:

- `ColourTheme.NONE`: No specific theme applied. When the theme is set to "None", this means we don't add a `theme-****` class to the page, and the default theme (_Coral_, at the time of writing these docs) is applied.
- `ColourTheme.CORAL`: Applies a `theme-coral` class to the page.
- `ColourTheme.LAGOON`: Applies a `theme-lagoon` class to the page.
- `ColourTheme.BANANA`: Applies a `theme-banana` class to the page.
- `ColourTheme.EARTH`: Applies a `theme-earth` class to the page.

???+ tip

    If additional themes are required, they can be added to the `tbx.core.utils.models.ColourTheme` enumeration.

## Theme configuration

The `tbx.core.utils.models.ColourThemeMixin` provides a mechanism for associating a specific colour theme with a page. It offers the following functionality:

- `theme` field: Adds a ForeignKey field to associate a specific colour theme with a page.
- `theme_class`: A cached property that determines the appropriate CSS class to apply to a page. It first checks if the page has a `theme` specified. If not, it traverses the page's ancestors to find the first page that has a `theme` specified, eventually defaulting to `ColourTheme.NONE`.

---

???+ note

    Please ensure that the [Editor's guide](https://docs.google.com/document/d/1PAWccdQ4tfaZsrEWmpDhvP3GH5RRmBOARFVp4b-kje8/edit?usp=sharing) is updated accordingly whenever any changes are made to this feature.
