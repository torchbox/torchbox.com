# Grid

The grid setup can be found in `sass/components/_grid.scss`.

The site uses a grid that changes with the breakpoints of the site. Above the large breakpoint `(min-width: 1023px)` the grid is split into 12 columns and below the large breakpoint the grid is split into 4 columns.

### CSS setup

```css
.grid {
  display: grid;
  grid-template-columns: $grid-gutters repeat(4, 1fr) $grid-gutters;
  max-width: $site-width; // 1500px
  margin: 0 auto;

  @include media-query(large) {
    grid-template-columns:
      $grid-gutters-large repeat(12, 1fr)
      $grid-gutters-large;
  }

  @include media-query(x-large) {
    grid-template-columns:
      $grid-gutters-x-large repeat(12, 1fr)
      $grid-gutters-x-large;
  }
}
```

Any alignment or spacing rules for a component should be added using BEM syntax with `grid` as the block selector:

```css
.grid {
  &__title {
    margin-bottom: $spacer-small;
    grid-column: 2 / span 4;

    @include media-query(large) {
      grid-column: 4 / span 9;
    }
  }
}
```
