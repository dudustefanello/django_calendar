from datetime import datetime, timezone

from django.test import TestCase

from django_calendar.models import Calendar, Event, RecurrencyRule


class CalendarTestCase(TestCase):

    def setUp(self):
        """ start_time: 31/08/2024 10:00
            end_time:   31/08/2024 11:00
        """
        self.calendar = Calendar.objects.create(summary='EventManagerTestCase')

        self.start_time = datetime(2024, 9, 1, 10, 0)
        self.end_time = datetime(2024, 9, 1, 11, 0)

        self.event = Event.objects.create(
            calendar=self.calendar,
            summary='EventManagerTestCase',
            dtstart=self.start_time,
            dtend=self.end_time,
        )


class SummaryMixinTestCase(CalendarTestCase):

    def test_str_a(self):
        self.assertEqual(str(self.event), 'EventManagerTestCase')


class EventManagerTestCase(CalendarTestCase):

    def test_list_by_date_a(self):
        rrule = 'FREQ=DAILY;INTERVAL=1'
        RecurrencyRule.objects.create_by_rrule(self.event, rrule)
        self.assertIn(self.event.id, Event.objects.list_by_date(datetime(2024, 9, 1), self.calendar))
        self.assertIn(self.event.id, Event.objects.list_by_date(datetime(2024, 9, 2), self.calendar))
        self.assertIn(self.event.id, Event.objects.list_by_date(datetime(2024, 9, 3), self.calendar))

        self.assertIn(self.event.id, [i[0] for i in self.calendar.event_list_by_date(datetime(2024, 9, 4))])
        self.assertIn(self.event.id, [i[0] for i in self.calendar.event_list_by_date(datetime(2024, 9, 5))])
        self.assertIn(self.event.id, [i[0] for i in self.calendar.event_list_by_date(datetime(2024, 9, 6))])

    def test_list_by_date_b(self):
        rrule = 'FREQ=DAILY;INTERVAL=2;UNTIL=20240927T130000Z'
        RecurrencyRule.objects.create_by_rrule(self.event, rrule)
        self.assertIn(self.event.id, Event.objects.list_by_date(datetime(2024, 9, 1), self.calendar))
        self.assertNotIn(self.event.id, Event.objects.list_by_date(datetime(2024, 9, 24), self.calendar))
        self.assertIn(self.event.id, Event.objects.list_by_date(datetime(2024, 9, 25), self.calendar))

        self.assertIn(self.event.id, [i[0] for i in self.calendar.event_list_by_date(datetime(2024, 9, 27))])
        self.assertNotIn(self.event.id, [i[0] for i in self.calendar.event_list_by_date(datetime(2024, 9, 28))])
        self.assertNotIn(self.event.id, [i[0] for i in self.calendar.event_list_by_date(datetime(2024, 9, 29))])

    def test_list_by_date_c(self):
        rrule = 'FREQ=WEEKLY;INTERVAL=1;BYDAY=SU;COUNT=10'
        rec = RecurrencyRule.objects.create_by_rrule(self.event, rrule)
        self.assertIn(self.event.id, Event.objects.list_by_date(datetime(2024, 9, 8), self.calendar))
        self.assertNotIn(self.event.id, Event.objects.list_by_date(datetime(2024, 9, 16), self.calendar))
        self.assertIn(self.event.id, Event.objects.list_by_date(datetime(2024, 9, 22), self.calendar))

    def test_list_by_date_d(self):
        rrule = 'FREQ=WEEKLY;INTERVAL=1;BYDAY=MO'
        RecurrencyRule.objects.create_by_rrule(self.event, rrule)
        data = datetime(2024, 9, 23)
        lista = Event.objects.list_by_date(data, self.calendar)
        self.assertIn(self.event.id, lista)
        self.assertEqual(lista[self.event.id]['dtstart'].month, data.month)
        self.assertEqual(lista[self.event.id]['dtstart'].day, data.day)

    def test_list_by_date_e(self):
        rrule = 'FREQ=MONTHLY;BYDAY=1SA'
        RecurrencyRule.objects.create_by_rrule(self.event, rrule)
        self.assertIn(self.event.id, Event.objects.list_by_date(datetime(2024, 9, 7), self.calendar))
        self.assertNotIn(self.event.id, Event.objects.list_by_date(datetime(2024, 10, 7), self.calendar))
        self.assertIn(self.event.id, Event.objects.list_by_date(datetime(2024, 10, 5), self.calendar))
        self.assertNotIn(self.event.id, Event.objects.list_by_date(datetime(2024, 10, 12), self.calendar))
        self.assertNotIn(self.event.id, Event.objects.list_by_date(datetime(2024, 10, 19), self.calendar))

    def test_list_by_date_f(self):
        rrule = 'FREQ=MONTHLY;BYDAY=1SU'
        RecurrencyRule.objects.create_by_rrule(self.event, rrule)

        self.assertIn(self.event.id, Event.objects.list_by_date(datetime(2024, 10, 6), self.calendar))
        self.assertIn(self.event.id, Event.objects.list_by_date(datetime(2024, 11, 3), self.calendar))
        self.assertIn(self.event.id, Event.objects.list_by_date(datetime(2024, 12, 1), self.calendar))

        self.assertNotIn(self.event.id, Event.objects.list_by_date(datetime(2024, 10, 20), self.calendar))
        self.assertNotIn(self.event.id, Event.objects.list_by_date(datetime(2024, 11, 10), self.calendar))
        self.assertNotIn(self.event.id, Event.objects.list_by_date(datetime(2024, 12, 15), self.calendar))
        self.assertNotIn(self.event.id, Event.objects.list_by_date(datetime(2024, 12, 29), self.calendar))

    def test_list_by_date_g(self):
        rrule = 'FREQ=YEARLY;INTERVAL=1;BYMONTH=8;BYDAY=3TH;COUNT=5'
        RecurrencyRule.objects.create_by_rrule(self.event, rrule)
        self.assertIn(self.event.id, Event.objects.list_by_date(datetime(2025, 8, 21), self.calendar))
        self.assertIn(self.event.id, Event.objects.list_by_date(datetime(2026, 8, 20), self.calendar))
        self.assertIn(self.event.id, Event.objects.list_by_date(datetime(2027, 8, 19), self.calendar))
        self.assertIn(self.event.id, Event.objects.list_by_date(datetime(2028, 8, 17), self.calendar))
        self.assertNotIn(self.event.id, Event.objects.list_by_date(datetime(2029, 8, 31), self.calendar))

    def test_list_by_date_h(self):
        rrule = 'FREQ=MONTHLY;INTERVAL=1;BYMONTHDAY=19;COUNT=4'
        RecurrencyRule.objects.create_by_rrule(self.event, rrule)
        self.assertIn(self.event.id, Event.objects.list_by_date(datetime(2024, 9, 19), self.calendar))
        self.assertIn(self.event.id, Event.objects.list_by_date(datetime(2024, 10, 19), self.calendar))
        self.assertNotIn(self.event.id, Event.objects.list_by_date(datetime(2024, 11, 20), self.calendar))

    def test_list_by_date_i(self):
        rrule = 'FREQ=YEARLY;INTERVAL=2;BYMONTH=10;BYMONTHDAY=19;COUNT=6'
        RecurrencyRule.objects.create_by_rrule(self.event, rrule)
        self.assertIn(self.event.id, Event.objects.list_by_date(datetime(2024, 10, 19), self.calendar))
        self.assertNotIn(self.event.id, Event.objects.list_by_date(datetime(2025, 10, 19), self.calendar))
        self.assertIn(self.event.id, Event.objects.list_by_date(datetime(2026, 10, 19), self.calendar))
        self.assertNotIn(self.event.id, Event.objects.list_by_date(datetime(2027, 10, 19), self.calendar))


class RecurrencyRuleManagerTestCase(CalendarTestCase):

    def test_str_a(self):
        rrule = 'FREQ=DAILY;INTERVAL=2'
        recurrency = RecurrencyRule.objects.create_by_rrule(self.event, rrule)
        self.assertEqual(str(recurrency), 'EventManagerTestCase')

    def test_create_by_rrule_a(self):
        rrule = 'FREQ=DAILY;INTERVAL=2'
        recurrency = RecurrencyRule.objects.create_by_rrule(self.event, rrule)
        self.assertEqual(recurrency.freq, 'DAILY')
        self.assertEqual(recurrency.interval, 2)

    def test_create_by_rrule_b(self):
        rrule = 'FREQ=DAILY;INTERVAL=1;UNTIL=20240927T000000Z'
        recurrency = RecurrencyRule.objects.create_by_rrule(self.event, rrule)
        self.assertEqual(recurrency.until, datetime(2024, 9, 27, 0, 0, tzinfo=timezone.utc))

    def test_create_by_rrule_c(self):
        rrule = 'FREQ=WEEKLY;INTERVAL=1;BYDAY=SU,TU,TH,SA;COUNT=10'
        recurrency = RecurrencyRule.objects.create_by_rrule(self.event, rrule)
        self.assertEqual(recurrency.freq, 'WEEKLY')
        self.assertEqual(recurrency.byday, 'SU,TU,TH,SA')
        self.assertIsNone(recurrency.until)
        self.assertEqual(recurrency.count, 10)

    def test_create_by_rrule_d(self):
        rrule = 'FREQ=MONTHLY;INTERVAL=1;BYDAY=1FR'
        recurrency = RecurrencyRule.objects.create_by_rrule(self.event, rrule)
        self.assertIsNone(recurrency.byday)
        self.assertEqual(recurrency.bymonthday, '1FR')

    def test_create_by_rrule_e(self):
        rrule = 'FREQ=MONTHLY;INTERVAL=1;BYMONTHDAY=5;UNTIL=20240928T000000Z'
        recurrency = RecurrencyRule.objects.create_by_rrule(self.event, rrule)
        self.assertEqual(recurrency.freq, 'MONTHLY')
        self.assertEqual(recurrency.bymonthdate, '5')
        self.assertEqual(recurrency.until, datetime(2024, 9, 28, 0, 0, tzinfo=timezone.utc))

    def test_create_by_rrule_f(self):
        rrule = 'FREQ=YEARLY;INTERVAL=3;BYMONTH=6;BYDAY=1FR,2MO'
        recurrency = RecurrencyRule.objects.create_by_rrule(self.event, rrule)
        self.assertEqual(recurrency.freq, 'YEARDAY')
        self.assertEqual(recurrency.bymonthday, '1FR,2MO')
        self.assertEqual(recurrency.bymonth, '6')

    def test_create_by_rrule_g(self):
        rrule = 'FREQ=YEARLY;INTERVAL=10;BYMONTH=12;BYMONTHDAY=7'
        recurrency = RecurrencyRule.objects.create_by_rrule(self.event, rrule)
        self.assertEqual(recurrency.interval, 10)
        self.assertEqual(recurrency.bymonth, '12')
        self.assertEqual(recurrency.bymonthdate, '7')
