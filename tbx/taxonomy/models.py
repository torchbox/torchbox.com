from django.db import models

from wagtail.admin.panels import FieldPanel, TitleFieldPanel
from wagtail.admin.widgets.slug import SlugInput


class BaseTaxonomy(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["sort_order"]
        abstract = True

    panels = [
        TitleFieldPanel("name"),
        FieldPanel("slug", widget=SlugInput),
        FieldPanel("description"),
        FieldPanel("sort_order"),
    ]


class Service(BaseTaxonomy):
    pass


class Sector(BaseTaxonomy):
    pass


class Team(BaseTaxonomy):
    pass
