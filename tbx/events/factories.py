import wagtail_factories

from tbx.events.models import EventIndexPage


class EventIndexPageFactory(wagtail_factories.PageFactory):
    title = "Events"
    no_events_message = "<p>No events at the moment.</p>"

    class Meta:
        model = EventIndexPage
