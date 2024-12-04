from django.utils.safestring import mark_safe

from bs4 import BeautifulSoup
from markdown import markdown


def get_inline_markdown(text):
    """Get markdown without the surrounding <p> tags."""
    if not text:
        return text

    # Strip all HTML tags to make sure we have clean text.
    soup = BeautifulSoup(text, "html5lib")
    text_only = soup.text

    # Convert markdown to HTML, remove paragraph tags.
    return mark_safe(markdown(text_only).replace("<p>", "").replace("</p>", ""))
