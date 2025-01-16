from wagtail.templatetags.wagtailcore_tags import register

from pattern_library.monkey_utils import override_tag


override_tag(register, name="include_block", default_html="")
override_tag(register, name="pageurl", default_html="/")
override_tag(register, name="slugurl", default_html="")
