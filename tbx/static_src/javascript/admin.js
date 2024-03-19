// JS for the wagtail admin

// customise options for the markdown block so only the code block is available
window.wagtailMarkdown = window.wagtailMarkdown || {};
window.wagtailMarkdown.options = window.wagtailMarkdown.options || {};
window.wagtailMarkdown.options.spellChecker = false;
window.wagtailMarkdown.options.toolbar = ['code'];
