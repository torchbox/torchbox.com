// This is a customised list of options to support when running `svgo` commands within the project - see docs/front-end/tooling.md for examples of commands you can run.

// The full list of options and explanations can be found at https://github.com/svg/svgo#built-in-plugins

// Commented out rules are in the default config but deliberately disabled in ours
module.exports = {
    js2svg: { useShortTags: false }, // add closing tags for ie11
    plugins: [
        'removeDoctype',
        'removeXMLProcInst',
        'removeComments',
        'removeMetadata',
        'removeEditorsNSData',
        'cleanupAttrs',
        'mergeStyles',
        'inlineStyles',
        'minifyStyles',
        // 'cleanupIDs', // Disabled so we can run svgo with the sprites.html file
        'removeUselessDefs',
        'cleanupNumericValues',
        'convertColors',
        'removeUnknownsAndDefaults',
        'removeNonInheritableGroupAttrs',
        'removeUselessStrokeAndFill',
        // 'removeViewBox', // We like view boxes thank you
        'cleanupEnableBackground',
        // 'removeHiddenElems', // Disabled so we can run svgo with the sprites.html file
        'removeEmptyText',
        'convertShapeToPath',
        'convertEllipseToCircle',
        'moveElemsAttrsToGroup',
        'moveGroupAttrsToElems',
        'collapseGroups',
        'convertPathData',
        'convertTransform',
        'removeEmptyAttrs',
        'removeEmptyContainers',
        'mergePaths',
        'removeUnusedNS',
        'sortDefsChildren',
        'removeTitle',
        'removeDesc',

        // The following extra rules enabled for our config but which are not in the default config
        'removeXMLNS', // xmlns definition is not needed for inline sprites or background images
        'removeDimensions', // convert width and height attributes to a viewBox attribute
        'removeRasterImages', // added because if you have an embedded png you should probably just save the file as a png
    ],
};
