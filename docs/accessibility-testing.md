# Accessibility testing

This build has a very high standard for accessibility testing. The merge request template and accessibility checklist in the [Monday ticket template](https://torchbox.monday.com/boards/1192293412/pulses/1349479497) contain prompts for what must be tested.

## Automated checks

Automated checks can be tested with the Axe browser plugin for [chrome](https://www.deque.com/axe/devtools/chrome-browser-extension) or [firefox](https://www.deque.com/axe/devtools/firefox-browser-extension/). There should be zero issues reported, both at desktop and mobile.

## HTML validation passes

Check by viewing the source code of the page you want to test, and pasting it into https://validator.w3.org/#validate_by_input. Note that occasionally there is an error reported for the largest rendition of a responsive image - this can happen if the image uploaded to the image library is smaller than the largest possible rendition, so we end up with two the same size.

## Manual checks

These checks should cover:

- tab order
- browser font-size settings (at the largest size)
- browser zoom
- keyboard focus must be always visible
- keyboard-only navigation
- link styles
- avoiding focus traps
- non-javascript options where appropriate
- decorative elements hidden from screen readers

## Screen reader testing

This can be tested in Voiceover in Safari, or in browserstack.

## High contrast mode

This can be tested in chrome. Open the inspector, and click on the 3 vertical dots top right. Choose 'more tools' then 'rendering'. Under 'Emulate CSS media forced-colors' switch to `forced-colors:active`. You can then test in both dark and light mode by switching the options under 'Emulate CSS media feature prefers-color-scheme'. All key information, links and hover states must be visible in high contrast mode. There are some media query mixins to add particular rules for high contrast mode if needed.

## Any animations removed for prefers-reduced-motion

You should ensure any animations and transitions added in CSS are removed for anyone who has chosen the 'reduced motion' option in their browser. This can also be tested in the 'rendering' area of the Chrome inspector, as described above. Choose the 'Emulate CSS media feature prefers-reduced-motion' option and switch to 'prefers-reduced-motion:reduce'. There is a media query mixin to add CSS rules for `prefers-reduced-motion`.
