from datetime import date

from django.contrib.sites.managers import CurrentSiteManager
from dateutil import parser


class EventManager(CurrentSiteManager):

    def list_by_date(self, datahr, calendar):
        result = {}
        for event in self.filter(calendar=calendar).order_by('dtstart'):
            datetimes = event.rrule.get_datetimes(event.dtstart.replace(hour=0, minute=0))
            lista = [date(d.year, d.month, d.day) for d in datetimes]
            data = date(datahr.year, datahr.month, datahr.day)
            if data in lista:
                result.update({event.id: event.get_object(data)})
        return result


class RecurrencyRuleManager(CurrentSiteManager):

    def create_by_rrule(self, event, rrule):
        rules = rrule.split(';')
        fields = {}
        for rule in rules:
            name, value = rule.split('=')
            fields.update({name.lower(): value})

        def get_freq():
            if fields['freq'] in ['DAILY', 'WEEKLY']:
                return fields['freq']
            if fields['freq'] == 'MONTHLY':
                if 'byday' in fields:
                    return 'MONTHDAY'
                return 'MONTHLY'
            if 'byday' in fields:
                return 'YEARDAY'
            return 'YEARLY'

        def get_repeat():
            if 'count' in fields:
                return 'COUNT'
            if 'until' in fields:
                return 'UNTIL'
            return None

        def get_until():
            until = fields.get('until', None)
            return None if not until else parser.isoparse(until)

        def get_count():
            count = fields.get('count', None)
            return None if not count else int(count)

        def get_byday():
            if fields['freq'] == 'WEEKLY':
                return fields.get('byday', None)
            return None

        def get_bymonth():
            if fields['freq'] == 'YEARLY':
                return fields.get('bymonth', None)
            return None
        
        def get_bymonthdate():
            if fields['freq'] in ['MONTHLY', 'YEARLY']:
                return fields.get('bymonthday', None)
            return None

        def get_bymonthday():
            if fields['freq'] in ['MONTHLY', 'YEARLY']:
                return fields.get('byday', None)
            return None

        return self.create(
            event=event,
            freq=get_freq(),
            interval=int(fields.get('interval', 1)),
            repeat=get_repeat(),
            until=get_until(),
            count=get_count(),
            byday=get_byday(),
            bymonth=get_bymonth(),
            bymonthdate=get_bymonthdate(),
            bymonthday=get_bymonthday(),
        )
