from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.utils import timezone
from django.utils.http import urlencode

from tbx.core.utils.fields import StreamField
from tbx.core.utils.models import ColourThemeMixin, SocialFields
from tbx.events.blocks import EventItemBlock
from tbx.people.models import ContactMixin
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Page


class EventIndexPage(ColourThemeMixin, ContactMixin, SocialFields, Page):
    template = "patterns/pages/events/events_listing.html"

    parent_page_types = ["torchbox.HomePage"]
    subpage_types = []

    events = StreamField([("event", EventItemBlock())], blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel("events"),
    ]

    promote_panels = (
        [
            MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        ]
        + ColourThemeMixin.promote_panels
        + ContactMixin.promote_panels
        + [
            MultiFieldPanel(SocialFields.promote_panels, "Social fields"),
        ]
    )

    def get_events(self, time_filter=None):
        today = timezone.localdate()
        if time_filter == "past":
            events = [
                event.value
                for event in self.events
                if event.value.get("start_date") < today
            ]
            events.sort(key=lambda x: x.get_start_date_time(), reverse=True)
        else:
            events = [
                event.value
                for event in self.events
                if today < event.value.get("start_date")
            ]
            events.sort(key=lambda x: x.get_start_date_time())
        return events

    def get_context(self, request):
        context = super().get_context(request)

        # Used for the purposes of defining the filterable tags
        tags = [
            {
                "name": "Upcoming events",
                "slug": "upcoming",
            },
            {
                "name": "Past events",
                "slug": "past",
            },
        ]

        slug_filter = request.GET.get("filter")
        events = self.get_events(slug_filter)

        # Use `page` to filter.
        page = request.GET.get("page", 1)

        # Pagination
        paginator = Paginator(events, 10)  # Show 10 events per page

        try:
            paged_events = paginator.page(page)
        except PageNotAnInteger:
            paged_events = paginator.page(1)
        except EmptyPage:
            paged_events = paginator.page(paginator.num_pages)

        extra_url_params = {}
        if slug_filter:
            extra_url_params["filter"] = slug_filter

        context.update(
            events=paged_events,
            extra_url_params=urlencode(extra_url_params),
            tags=tags,
        )
        return context
