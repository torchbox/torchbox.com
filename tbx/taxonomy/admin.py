from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from . import models


class ServiceModelAdmin(SnippetViewSet):
    model = models.Service
    base_url_path = "taxonomy/service"
    menu_icon = "info-circle"
    icon = "info-circle"
    list_display = ("name", "slug", "sort_order")
    ordering = ["sort_order"]


class TeamModelAdmin(SnippetViewSet):
    model = models.Team
    base_url_path = "taxonomy/team"
    menu_icon = "group"
    icon = "group"
    list_display = ("name", "slug", "sort_order")
    ordering = ["sort_order"]


class SectorModelAdmin(SnippetViewSet):
    model = models.Sector
    base_url_path = "taxonomy/sector"
    menu_icon = "globe"
    icon = "globe"
    list_display = ("name", "slug", "sort_order")
    ordering = ["sort_order"]


class TaxonomyModelAdminGroup(SnippetViewSetGroup):
    menu_label = "Taxonomy"
    menu_icon = "folder-open-inverse"
    menu_order = 750
    items = [ServiceModelAdmin, SectorModelAdmin, TeamModelAdmin]
