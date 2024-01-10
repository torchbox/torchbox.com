# Fonts

The site uses 'Outfit' as the main font and 'sans-serif' as the fallback font.

Outfit is avaible from [Google Fonts](https://fonts.google.com/specimen/Outfit) and is a variable font. This means that the font can be loaded as a single file and the weight and style can be adjusted using CSS. Any weight between 300 and 600 can be used however we recommend using 300, 400 and 600 for light, regular and semi-bold respectively.

We originally limited the number of font variants for reasons of sustainability, although the fact that this is a variable font means that extra weights could be added if required without impacting carbon emissions. However, for design reasons it is probably best to stick to these three.

The font is loaded using the following CSS in `sass/base/_fonts.scss`:

```css
@font-face {
  font-family: 'Outfit';
  font-style: normal;
  font-weight: 300 600;
  font-display: swap;
  src: url(../fonts/outfit-variable-font.woff2) format('woff2-variations');
}
```
