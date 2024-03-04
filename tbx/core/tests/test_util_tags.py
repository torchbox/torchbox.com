from datetime import datetime, time

from django.test import SimpleTestCase

from tbx.core.templatetags.util_tags import format_date_for_event


class TestFormatDateForEvent(SimpleTestCase):
    def test_with_start_date_only(self):
        self.assertEqual(
            format_date_for_event(datetime(2021, 1, 1).date(), None, None, None),
            "1 Jan 2021",
        )

    def test_with_start_date_and_start_time(self):
        self.assertEqual(
            format_date_for_event(datetime(2021, 1, 1).date(), time(13, 0), None, None),
            "1 Jan 2021, 1pm",
        )

    def test_with_start_date_and_end_date(self):
        self.assertEqual(
            format_date_for_event(
                datetime(2021, 1, 1).date(), None, datetime(2021, 1, 2).date(), None
            ),
            "1 Jan 2021 - 2 Jan 2021",
        )

    def test_with_start_date_and_start_time_and_end_date_and_end_time_on_same_day(self):
        self.assertEqual(
            format_date_for_event(
                datetime(2021, 1, 1).date(),
                time(13, 0),
                datetime(2021, 1, 1).date(),
                time(14, 0),
            ),
            "1 Jan 2021, 1-2pm",
        )

    def test_with_start_date_and_start_time_and_end_date_on_same_day_with_different_time_suffix(
        self,
    ):
        self.assertEqual(
            format_date_for_event(
                datetime(2021, 1, 1).date(),
                time(11, 0),
                datetime(2021, 1, 1).date(),
                time(14, 0),
            ),
            "1 Jan 2021, 11am-2pm",
        )

    def test_with_start_date_and_start_time_and_end_date_and_end_time_on_different_day(
        self,
    ):
        self.assertEqual(
            format_date_for_event(
                datetime(2021, 1, 1).date(),
                time(13, 0),
                datetime(2021, 1, 2).date(),
                time(14, 0),
            ),
            "1 Jan 2021, 1pm - 2 Jan 2021, 2pm",
        )

    def test_with_start_date_and_start_time_and_end_date_on_different_day_with_different_time_suffix(
        self,
    ):
        self.assertEqual(
            format_date_for_event(
                datetime(2021, 1, 1).date(),
                time(11, 0),
                datetime(2021, 1, 2).date(),
                time(14, 0),
            ),
            "1 Jan 2021, 11am - 2 Jan 2021, 2pm",
        )

    def test_with_start_date_and_end_date_and_end_time_on_same_day(
        self,
    ):
        self.assertEqual(
            format_date_for_event(
                datetime(2021, 1, 1).date(),
                None,
                datetime(2021, 1, 1).date(),
                time(14, 0),
            ),
            "1 Jan 2021, 2pm",
        )

    def test_with_start_date_and_end_date_and_end_time_on_different_day(self):
        self.assertEqual(
            format_date_for_event(
                datetime(2021, 1, 1).date(),
                None,
                datetime(2021, 1, 2).date(),
                time(14, 0),
            ),
            "1 Jan 2021 - 2 Jan 2021, 2pm",
        )
