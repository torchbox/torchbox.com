import datetime
from itertools import chain

from django import forms
from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from tbx.core.utils.models import ColourThemeMixin, SocialFields
from tbx.taxonomy.models import Sector, Service
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.models import Orderable, Page


class EventIndexPage(ColourThemeMixin, SocialFields, Page):
    template = "patterns/pages/events/events_listing.html"

    parent_page_types = ["torchbox.HomePage"]
    subpage_types = []

    content_panels = Page.content_panels + [
        InlinePanel("events", label="events"),
    ]

    promote_panels = (
        [
            MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        ]
        + ColourThemeMixin.promote_panels
        + [
            MultiFieldPanel(SocialFields.promote_panels, "Social fields"),
        ]
    )

    def get_events(self, taxonomy_filter=None):
        today = datetime.date.today()
        events = self.events.exclude(date__lt=today)
        if taxonomy_filter:
            events = events.filter(
                Q(related_services__slug=taxonomy_filter)
                | Q(related_services__slug=taxonomy_filter)
            )
        return events.order_by("date")

    def get_context(self, request):
        context = super().get_context(request)
        related_sectors = Sector.objects.all()
        related_services = Service.objects.all()

        # Used for the purposes of defining the filterable tags
        tags = related_sectors.union(related_services)

        context.update(
            events=self.get_events(request.GET.get("filter")),
            tags=tags,
        )
        return context


class Event(ClusterableModel, Orderable):
    page = ParentalKey(EventIndexPage, related_name="events")
    title = models.CharField(max_length=255)
    intro = models.TextField(verbose_name="Description")
    link_external = models.URLField("External link")
    date = models.DateField("Event date")
    event_type = models.CharField(max_length=30)
    author = models.ForeignKey(
        "people.Author",
        on_delete=models.SET_NULL,
        null=True,
        related_name="authors",
        verbose_name="Host",
    )
    related_sectors = ParentalManyToManyField("taxonomy.Sector", related_name="events")

    related_services = ParentalManyToManyField(
        "taxonomy.Service", related_name="events"
    )

    @cached_property
    def sectors(self):
        return self.related_sectors.all()

    @cached_property
    def services(self):
        return self.related_services.all()

    @property
    def tags(self):
        return chain(self.services, self.sectors)

    panels = [
        FieldPanel("title"),
        FieldPanel("intro"),
        FieldPanel("link_external"),
        FieldPanel("author"),
        FieldPanel("date"),
        FieldPanel("event_type"),
        FieldPanel("related_sectors", widget=forms.CheckboxSelectMultiple),
        FieldPanel("related_services", widget=forms.CheckboxSelectMultiple),
    ]
