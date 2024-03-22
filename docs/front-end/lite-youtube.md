# Lite youtube

We use the https://www.npmjs.com/package/lite-youtube-embed package to avoid setting youtube cookies, along with https://theorangeone.net/projects/wagtail-lite-youtube-embed/

When youtube videos are first loaded the user must accept the youtube Ts and Cs. They can opt not to show them again - this sets a cookie to hide the consent message in future.

This functionality is controlled by `tbx/static_src/javascript/components/youtube-embed.js`.
