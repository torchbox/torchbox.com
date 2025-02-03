from django.db import models

from wagtail.admin.panels import FieldPanel, TitleFieldPanel


class BaseTaxonomy(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField()

    class Meta:
        ordering = ["sort_order"]
        abstract = True

    def __str__(self) -> str:
        return self.name

    panels = [
        TitleFieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("description"),
        FieldPanel("sort_order"),
    ]


class Service(BaseTaxonomy):
    """Represents a service that Torchbox offers to clients

    This will be assigned to blog posts and work articles, and users will be able to filter by service
    """


class Sector(BaseTaxonomy):
    """Represents a sector that Torchbox works in

    This will be assigned to blog posts and work articles, and users will be able to filter by sector
    """


class Team(BaseTaxonomy):
    """Represents each team that makes up Torchbox

    A person may be assigned to one or more teams. Teams are used to filter the team listing page
    """
