# Navigation

At the top level, the main navigation links are determined by the primary navigation settings.

In these settings there is a dropdown to allow configuration of how many children to show - one of:

- 'Do not show child pages',
- 'Show child pages up to level 1 (children)',
- 'Show child pages up to level 2 (grandchildren)'.

If the 'Do not show child pages' option is chosen, then there will be no drop down at desktop - this is useful for 'work' and 'thinking' sections where there are many child pages.

If 'Show child pages up to level 1 (children)' is selected, then a small dropdown will show at desktop, with just one level of child pages.

If 'Show child pages up to level 2 (grandchildren)' is selected, then a mega dropdown appears at desktop showing children and grandchildren.

Whether lower level navigation links are displayed or not determined by whether a given page has 'show in menu' selected. The navigation shows up to the grandchildren of the primary navigation items, and no lower.

The desktop and mobile menus have two separate sets of markup in the html, and separate mobile and desktop CSS to make them easier to maintain. The smaller (level 1 only) desktop menu also has its own separate markup and CSS.

On the front-end, at desktop, the primary navigation links (the ones at the top level) display across the top of the page in the header. The lower levels are revealed when clicking on one of the primary links. This functionality is controlled by `desktop-sub-menu.js`.

At mobile, the primary links are hidden by default. They appear in a drop-down menu when the menu toggle is clicked - controlled by `mobile-menu.js`. When a parent primary menu item is clicked, the sub-navigation menu is opened, and then if a sub-navigation item with children is clicked, a third level is revealed. The second and third levels are controlled by `mobile-sub-menu.js`.
