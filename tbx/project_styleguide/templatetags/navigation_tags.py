from pattern_library.monkey_utils import override_tag
from tbx.navigation.templatetags.navigation_tags import register

override_tag(register, name="primarynav", default_html="")
override_tag(register, name="primarynavmobile", default_html="")
override_tag(register, name="footerlinks", default_html="")
