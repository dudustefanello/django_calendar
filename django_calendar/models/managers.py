from datetime import date

from django.contrib.sites.managers import CurrentSiteManager
from django.utils.translation import gettext_lazy as _
from dateutil import parser


class EventManager(CurrentSiteManager):

    def list_by_date(self, datahr):
        result = {}
        for event in self.all():
            lista = [date(d.year, d.month, d.day) for d in event.rrule.get_datetimes(
                datahr.replace(hour=23, minute=59, tzinfo=event.dtstart.tzinfo)
            )]
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
            if 'freq' not in fields:
                raise AttributeError(_('Parâmetro obrigatório FREQ não informado'))
            return fields['freq']

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
            if 'byday' in fields:
                if fields['freq'] == 'DAILY':
                    raise AttributeError(_('Parâmetro BYDAY não deve ser informado para frequência Diária'))

                bw = bd = ''
                for byday in fields['byday'].split(','):
                    if byday.startswith('-1'):
                        bw += ('' if bw == '' else ',') + byday[0:2]
                        bd += ('' if bd == '' else ',') + byday[2:]
                    elif byday[0].isdigit():
                        bw += ('' if bw == '' else ',') + byday[0:1]
                        bd += ('' if bd == '' else ',') + byday[1:]
                    else:
                        bw += ('' if bd == '' else ',') + ''
                        bd += ('' if bd == '' else ',') + byday
                return bw, bd
            return None, None

        def get_bymonth():
            if fields['freq'] != 'YEARLY' and 'bymonth' in fields:
                raise AttributeError(_('Parâmetro BYMONTH só deve ser informado para frequência Anual'))
            return fields.get('bymonth', None)

        def get_bymonthday():
            if (fields['freq'] == 'DAILY' or fields['freq'] == 'WEEKLY') and 'bymonthday' in fields:
                raise AttributeError(_('Parâmetro BYMONTHDAY só deve ser informado para frequência Anual'))
            bymonthday = fields.get('bymonthday', None)
            return None if not bymonthday else int(bymonthday)

        byweek, byday = get_byday()
        return self.create(
            event=event,
            freq=get_freq(),
            interval=int(fields.get('interval', 1)),
            repeat=get_repeat(),
            until=get_until(),
            count=get_count(),
            byday=byday,
            byweek=byweek,
            bymonth=get_bymonth(),
            bymonthday=get_bymonthday(),
        )
