from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.http import urlencode

from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField

from tbx.core.models import BasePage
from tbx.core.utils.fields import StreamField
from tbx.events.blocks import EventItemBlock


class EventIndexPage(BasePage):
    template = "patterns/pages/events/events_listing.html"
    no_events_message = RichTextField(
        features=["bold", "italic", "link", "superscript", "subscript"],
        help_text="Message to display if there are no events",
    )

    parent_page_types = ["torchbox.HomePage"]
    subpage_types = []

    events = StreamField([("event", EventItemBlock())], blank=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("no_events_message"),
        FieldPanel("events"),
    ]

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
        paged_events = paginator.get_page(page)

        extra_url_params = {}
        if slug_filter:
            extra_url_params["filter"] = slug_filter

        context.update(
            events=paged_events,
            extra_url_params=urlencode(extra_url_params),
            tags=tags,
        )
        return context
