# Front end tooling

## What's required

To install node on the host machine we recommend using [`nvm`](https://github.com/creationix/nvm). Once you have `nvm` installed simply run `nvm install` to install and activate the version of node required for the project. Refer to the [`nvm` documentation](https://github.com/creationix/nvm#usage) for more details about available commands.

## What's included

- [Sass](https://sass-lang.com/) CSS with [auto-prefixing](https://github.com/postcss/autoprefixer).
- [Tailwind CSS](https://tailwindcss.com/), via its PostCSS plugin.
- [TypeScript](https://www.typescriptlang.org/) for ES2015+ JavaScript, and TypeScript support.
- [webpack-dev-server](https://webpack.js.org/configuration/dev-server/) for autoreloading.
- [Webpack](https://webpack.js.org/) for module bundling.
  - With `ts-loader` to process JavaScript and TypeScript.
  - With `css-loader`, `postcss-loader`, and `sass-loader` to process stylesheets.
- Consideration for images, currently copying the directory only - to avoid slowdowns and non-essential dependencies. We encourage using SVG for UI vectors and pre-optimised UI photograph assets.
- [Build commands](#build-scripts) for generating testable or deployable assets only
- CSS linting with `stylelint`
- JS linting with `Biome`
- [Jest](https://jestjs.io/) for JavaScript unit tests.

## Developing with it

- To start the development environment, follow the instructions in README.md in the project root
- Source files for developing your project are in `static_src` and the distribution folder for the compiled assets is `static_compiled`. Don't make direct changes to the `static_compiled` directory as they will be overwritten.

## Tests

JavaScript unit tests for this project use [Jest](https://jestjs.io/). Here are commands you can use:

```sh
# Run the whole test suite once.
pnpm run test
# Run the whole test suite, collecting test coverage information.
pnpm run test:coverage
# Start Jest in watch mode, to run tests on a subset of the files.
pnpm run test:watch
```

## Deploying it

### Build scripts

To only build assets for either development or production you can use

- `pnpm run build` To build development assets
- `pnpm run build:prod` To build assets with minification and vendor prefixes

## Third party libraries

We no longer have a 'vendor' folder for these. Instead find ones that are packaged as npm libraries and install them as dependencies with `pnpm add`. If they have CSS that needs including, this can be imported directly from the node_modules folder.

## CSS background images

There is a folder inside `images` called `cssBackgrounds` where you should place any images referenced by the CSS, whether svg, jpg or png. The tooling will detect the image size, and if it is small (less than 1024 bytes), then it will be automatically encoded within the compiled CSS file. Larger images will be synced to the `cssBackgrounds` folder and referenced in the compiled CSS as a separate file.

## Minimising images

We do not include image minimisation as part of the toolchain out the box for these reasons:

- Developers should always check the quality of images has not been impacted after running the commands
- The packages involved are large
- Minimising images on watch would slow the toolchain down considerably

However, you can install the required packages on your local machine and run the minimisation yourself from the command line by following these instructions.

### Minimising svgs

We provide a config file for svgo, `svgo.config.js` in the project root, which has some recommended presets - but always check the file after running the minimising command to check it has not removed any code that you need.

First, install svgo globally if you have not done this previously:

```sh
pnpm add -g svgo
```

You can then run the `svgo` command from the terminal. Here are some examples:

- From the root folder of the project, target all svg files in the `static_src/images` folder and all subfolders. This will automatically detect the config file and overwrite the files with the new versions:

  ```sh
  svgo -r -f tbx/static_src/images
  ```

- From the root folder of the project, target a specific svg file and put the output file in another folder for comparison (don't commit this file or folder to git). This will automatically detect the config file:

  ```sh
  svgo tbx/static_src/images/[your-file.svg] -o ./tbx/static_src/optimised_images
  ```

- From the same folder as the sprites file, minimise all the svgs in the file (check them all afterwards!). This will automatically detect the config file:

  ```sh
  svgo sprites.html
  ```

If you run the command from outside the project root you may need to pass an explict reference to the config file with the `--config` option.

Full svgo reference: <https://www.npmjs.com/package/svgo>

## Minimising jpgs and pngs

First, globally install imagemin and imagemin-mozjpeg if you have not done so before. We use the lossy mozjpeg plugin because the default (lossless), imagemin-jpegtran, can result in larger images than the original.

```sh
pnpm add -g imagemin-cli imagemin-mozjpeg imagemin-pngquant
```

You can then run the `imagemin` command from the terminal. Here are some examples:

- From the root folder of the project, minimise all jpegs in the `images` folder. The files will be overwritten by the new version:

  ```sh
  imagemin 'tbx/static_src/images/*.{jpg,jpeg}' --plugin=mozjpeg --out-dir=./tbx/static_src/images
  ```

- From the root folder of the project, target a specific jpeg file and output it into another folder for comparison (don't commit this file or folder to git):

  ```sh
  imagemin tbx/static_src/images/[your-file.jpg] --plugin=mozjpeg --out-dir=./tbx/static_src/optimised_images
  ```

- Minimise a particular png file and output a new version of it. This uses the lossy pngquant plugin instead of the default lossless plugin for better file size reduction:

  ```sh
  imagemin your-file.png --plugin=pngquant > your-file-optimised.png
  ```

References:

- Full imagemin-cli reference: <https://github.com/imagemin/imagemin-cli>
- Useful summary table of the plugins: <https://web.dev/use-imagemin-to-compress-images/#plugins>

## Further details of the packages included

- **@biomejs/biome** - lint and format your JavaScript, TypeScript and JSON, configured in `biome.jsonc` <https://biomejs.dev/>
- **@tailwindcss/postcss** - runs Tailwind CSS as a PostCSS plugin <https://tailwindcss.com/docs/installation/using-postcss>
- **autoprefixer** - adds vendor prefixes as necessary for the browsers defined in `browserslist` in `package.json` <https://www.npmjs.com/package/autoprefixer>
- **copy-webpack-plugin** - used to sync images from static_src to static_compiled
- **css-loader** - add support for Webpack to load stylesheets
- **cssnano** - minify CSS with safe optimisations <https://cssnano.co/>
- **jest** - testing framework for JavaScript <https://jestjs.io/>
- **mini-css-extract-plugin** - extract CSS generated by Webpack into separate files
- **postcss-custom-properties** - polyfill for CSS custom properties <https://www.npmjs.com/package/postcss-custom-properties>
- **postcss-loader** - integrate PostCSS preprocessing into Webpack's styles loading
- **prettier** - formats Markdown, CSS, SCSS and YAML <https://prettier.io/>
- **sass** and **sass-loader** - compile Sass and integrate it into Webpack's styles loading
- **stylelint** - linting for styles <https://stylelint.io>
- **stylelint-config-torchbox** - our custom rules for linting styles
- **stylelint-webpack-plugin** - runs stylelint as part of the Webpack build
- **ts-jest** - TypeScript support for Jest
- **ts-loader** - use TypeScript with webpack <https://www.npmjs.com/package/ts-loader>
- **typescript** - TypeScript compiler, defines which version of the language we use
- **webpack** - bundler for js files (can do much more too) <https://webpack.js.org/concepts/>
- **webpack-bundle-analyzer** - writes a bundle size report to `bundle-report.html` and opens it in your browser when you run `pnpm run build:analyse`
- **webpack-cli** - the webpack command calls this behind the scenes <https://www.npmjs.com/package/webpack-cli>
- **webpack-dev-server** - serves the build with live reload for `pnpm run start:reload`

Background images and fonts are handled by Webpack 5's built-in [asset modules](https://webpack.js.org/guides/asset-modules/), so there's no file-loader or url-loader.
