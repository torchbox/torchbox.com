# Navigation

At the top level, the main navigation links are determined by the primary navigation settings. These include an option to hide any child items - as the 'work' and 'thinking' top level links should never show their children.

Lower level navigation links are determined by whether a given page has 'show in menu' selected. These show up to a maximum of 3 levels, and no lower.

The desktop and mobile menus have two separate sets of markup in the html, but share the same classes, so the CSS must handle both the desktop and mobile styles.

On the front-end, at desktop, the primary navigation links (the ones at the top level) display across the top of the page in the header. The second and third levels are revealed together when clicking on one of the primary links. This functionality is controlled by `desktop-sub-menu.js`.

At mobile, the primary links are hidden by default. They appear in a drop-down menu when the menu toggle is clicked - controlled by `mobile-menu.js`. When a parent primary menu item is clicked, the sub-navigation menu is opened, and then if a sub-navigation item with children is clicked, a third level is revealed. The second and third levels are controlled by `mobil-sub-menu.js`.
