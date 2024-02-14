from pattern_library.monkey_utils import override_tag
from wagtail.images.templatetags.wagtailimages_tags import register

override_tag(register, name="image", default_html="")
override_tag(register, name="srcset_image", default_html="")
