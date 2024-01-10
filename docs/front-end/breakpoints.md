# Breakpoints

Breakpoints are used to define the responsive behavior of the site.

They are set in `static_src/sass/config/_variables.scss` and are defined as a map of key value pairs, where the key is the name of the breakpoint and the value is the minimum width of the breakpoint in pixels.

The breakpoints we use are:

```scss
$breakpoints: (
  'medium' '(min-width: 599px)',
  'large' '(min-width: 1023px)',
  'x-large' '(min-width: 1280px)'
);
```

Other breakpoints can be added to this map as required, however the breakpoints should be used sparingly and only when the design requires it.
