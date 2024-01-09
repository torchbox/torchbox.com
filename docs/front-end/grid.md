## Grid

The grid setup can be found in `sass/components/_grid.scss`.

The site uses a grid that changes with the breakpoints of the site. Above the large breakpoint `(min-width: 1023px)` the grid is split into 12 columns and below the large breakpoint the grid is split into 4 columns.

The column gap and gutter space also changes with the breakpoints:

### Column gap

```css
.grid {
  column-gap: 30px;

  @include media-query(large) {
    column-gap: 50px;
  }

  @include media-query(x-large) {
    column-gap: 80px;
  }
}
```

### Gutter space

```css
.grid {
  padding-left: 30px;
  padding-right: 30px;

  @include media-query(large) {
    padding-left: 80px;
    padding-right: 80px;
  }

  @include media-query(x-large) {
    padding-left: 120px;
    padding-right: 120px;
  }
}
```

### Site width

The maximum site-width is `1500px`.
