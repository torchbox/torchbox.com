from bs4 import BeautifulSoup


def convert_bold_links_to_pink(html_text):
    """Convert <b> tags inside links into <span class="text-coral">."""
    soup = BeautifulSoup(html_text, "html.parser")
    for anchor_tag in soup.find_all("a"):
        for bold_tag in anchor_tag.find_all("b"):
            tag_content = "".join([str(c) for c in bold_tag.contents])
            html_text = html_text.replace(
                str(bold_tag), f'<span class="text-coral">{tag_content}</span>'
            )
    return html_text


def convert_italic_links_to_purple(html_text):
    """Convert <i> tags inside links into <span class="text-nebuline">."""
    soup = BeautifulSoup(html_text, "html.parser")
    for anchor_tag in soup.find_all("a"):
        for italic_tag in anchor_tag.find_all("i"):
            tag_content = "".join([str(c) for c in italic_tag.contents])
            html_text = html_text.replace(
                str(italic_tag), f'<span class="text-nebuline">{tag_content}</span>'
            )
    return html_text
