import uuid

from dateutil import rrule
from django.db import models
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField

from django_calendar.models.managers import EventManager, RecurrencyRuleManager
from django_calendar.models.mixins import BaseModel, DescriptionMixin, SiteMixin, SummaryMixin


class Calendar(BaseModel, SummaryMixin):
    uid = models.UUIDField(
        default=uuid.uuid4, unique=True, auto_created=True, editable=False, verbose_name=_('id único'),
    )

    def event_list_by_date(self, date):
        list_by_date = []
        events = Event.objects.list_by_date(date, self)
        for event in events:
            list_by_date.append((event, events[event]))
        return list_by_date

    class Meta(BaseModel.BaseMeta):
        verbose_name = _('calandário')
        verbose_name_plural = _('calendários')


class Event(BaseModel, SummaryMixin, DescriptionMixin):
    calendar = models.ForeignKey(to='calendar.Calendar', on_delete=models.CASCADE, verbose_name=_('calendário'))
    uid = models.UUIDField(default=uuid.uuid4, auto_created=True, editable=False, verbose_name=_('id único'))
    dtstart = models.DateTimeField(verbose_name=_('data e hora inicial'))
    dtend = models.DateTimeField(verbose_name=_('data e hora final'))
    status = models.CharField(max_length=12, default='CONFIRMED', choices=[
        ('TENTATIVE', _('Tentativa')),
        ('CONFIRMED', _('Confirmado')),
        ('CANCELLED', _('Cancelado')),
    ])
    sequence = models.PositiveSmallIntegerField(default=0, verbose_name=_('versão'))

    objects = EventManager()

    def get_object(self, data):
        return {
            'uid': self.uid,
            'summary': self.summary,
            'dtstart': self.dtstart.replace(year=data.year, month=data.month, day=data.day),
            'dtend': self.dtend.replace(year=data.year, month=data.month, day=data.day),
            'status': self.status,
        }

    class Meta(BaseModel.BaseMeta):
        verbose_name = _('evento')
        verbose_name_plural = _('eventos')


class ExDate(SiteMixin):
    event = models.ForeignKey(to='calendar.Event', on_delete=models.CASCADE, related_name='exdate')
    exdate = models.DateTimeField()

    class Meta(BaseModel.BaseMeta):
        verbose_name = _('data excluída')
        verbose_name_plural = _('datas excluídas')


class RecurrencyRule(SiteMixin):
    event = models.OneToOneField(
        to='calendar.Event', on_delete=models.CASCADE, related_name='rrule', verbose_name=_('evento'),
    )
    freq = models.CharField(max_length=8, choices=[
        ('DAILY', _('Diária')),
        ('WEEKLY', _('Semanal')),
        ('MONTHLY', _('Mensal (data)')),
        ('MONTHDAY', _('Mensal (mês)')),
        ('YEARLY', _('Anual (data)')),
        ('YEARDAY', _('Anual (mês)')),
    ], default='DAILY', verbose_name=_('frequência'))
    interval = models.PositiveSmallIntegerField(default=1, verbose_name=_('intervalo'))
    repeat = models.CharField(max_length=5, null=True, blank=True, choices=[
        (None, _('Para sempre')),
        ('UNTIL', _('Até a data')),
        ('COUNT', _('Quantidade de ocorrências')),
    ], verbose_name=_('Tipo de repetição'))
    until = models.DateTimeField(
        null=True, blank=True, verbose_name=_('até a data'),
        help_text=_('Utilizar apenas para Tipo de repetição "Até a data".'),
    )
    count = models.PositiveIntegerField(
        null=True, blank=True, verbose_name=_('quantidade de ocorrências'),
        help_text=_('Utilizar apenas para Tipo de repetição "Quantidade de ocorrências".'),
    )
    byday = MultiSelectField(
        null=True, blank=True, choices=[
            ('SU', _('Domingo')),
            ('MO', _('Segunda')),
            ('TU', _('Terça')),
            ('WE', _('Quarta')),
            ('TH', _('Quinta')),
            ('FR', _('Sexta')),
            ('SA', _('Sábado')),
        ], verbose_name=_('dias da semana'),
        help_text=_('Utilizar para frequência "Semanal", "Mensal" ou "Anual".'),
    )
    bymonth = MultiSelectField(
        null=True, blank=True, choices=[
            ('1', _('Janeiro')),
            ('2', _('Fevereiro')),
            ('3', _('Março')),
            ('4', _('Abril')),
            ('5', _('Maio')),
            ('6', _('Junho')),
            ('7', _('Julho')),
            ('8', _('Agosto')),
            ('9', _('Setembro')),
            ('10', _('Outubro')),
            ('11', _('Novembro')),
            ('12', _('Dezembro')),
        ], verbose_name=_('mês'),
        help_text=_('Utilizar para frequência "Anual".'),
    )
    bymonthdate = MultiSelectField(
        null=True, blank=True, choices=[
            ('1', _('1')),
            ('2', _('2')),
            ('3', _('3')),
            ('4', _('4')),
            ('5', _('5')),
            ('6', _('6')),
            ('7', _('7')),
            ('8', _('8')),
            ('9', _('9')),
            ('10', _('10')),
            ('11', _('11')),
            ('12', _('12')),
            ('13', _('13')),
            ('14', _('14')),
            ('15', _('15')),
            ('16', _('16')),
            ('17', _('17')),
            ('18', _('18')),
            ('19', _('19')),
            ('20', _('20')),
            ('21', _('21')),
            ('22', _('22')),
            ('23', _('23')),
            ('24', _('24')),
            ('25', _('25')),
            ('26', _('26')),
            ('27', _('27')),
            ('28', _('28')),
            ('29', _('29')),
            ('30', _('30')),
            ('31', _('31')),
        ], verbose_name=_('data do mês'),
    )
    bymonthday = MultiSelectField(
        null=True, blank=True, choices=[
            ('1SU', _('1º Domingo')),
            ('1MO', _('1ª Segunda')),
            ('1TU', _('1ª Terça')),
            ('1WE', _('1ª Quarta')),
            ('1TH', _('1ª Quinta')),
            ('1FR', _('1ª Sexta')),
            ('1SA', _('1º Sábado')),
            ('2SU', _('2º Domingo')),
            ('2MO', _('2ª Segunda')),
            ('2TU', _('2ª Terça')),
            ('2WE', _('2ª Quarta')),
            ('2TH', _('2ª Quinta')),
            ('2FR', _('2ª Sexta')),
            ('2SA', _('2º Sábado')),
            ('3SU', _('3º Domingo')),
            ('3MO', _('3ª Segunda')),
            ('3TU', _('3ª Terça')),
            ('3WE', _('3ª Quarta')),
            ('3TH', _('3ª Quinta')),
            ('3FR', _('3ª Sexta')),
            ('3SA', _('3º Sábado')),
            ('4SU', _('4º Domingo')),
            ('4MO', _('4ª Segunda')),
            ('4TU', _('4ª Terça')),
            ('4WE', _('4ª Quarta')),
            ('4TH', _('4ª Quinta')),
            ('4FR', _('4ª Sexta')),
            ('4SA', _('4º Sábado')),
            ('5SU', _('5º Domingo')),
            ('5MO', _('5ª Segunda')),
            ('5TU', _('5ª Terça')),
            ('5WE', _('5ª Quarta')),
            ('5TH', _('5ª Quinta')),
            ('5FR', _('5ª Sexta')),
            ('5SA', _('5º Sábado')),
            ('1SU', _('Último Domingo')),
            ('1MO', _('Última Segunda')),
            ('1TU', _('Última Terça')),
            ('1WE', _('Última Quarta')),
            ('1TH', _('Última Quinta')),
            ('1FR', _('Última Sexta')),
            ('1SA', _('Último Sábado')),
        ], verbose_name=_('dia do mês'),
    )

    objects = RecurrencyRuleManager()

    def get_datetimes(self, dtstart):
        return rrule.rrulestr(self.get_rule_string(), dtstart=dtstart)
    
    def get_rule_string(self):
        rrule = 'RRULE:'

        match self.freq:
            case 'DAILY':
                rrule += 'FREQ=DAILY;INTERVAL={}'.format(self.interval)
            case 'WEEKLY':
                rrule += 'FREQ=WEEKLY;INTERVAL={}'.format(self.interval)
                if self.byday:
                    rrule += ';BYDAY={}'.format(','.join(self.byday))
            case 'MONTHLY':
                rrule += 'FREQ=MONTHLY;INTERVAL={}'.format(self.interval)
                if self.bymonthdate:
                    rrule += ';BYMONTHDAY={}'.format(','.join(self.bymonthdate))
            case 'MONTHDAY':
                rrule += 'FREQ=MONTHLY;INTERVAL={}'.format(self.interval)
                if self.bymonthday:
                    rrule += ';BYDAY={}'.format(','.join(self.bymonthday))
            case 'YEARLY':
                rrule += 'FREQ=YEARLY;INTERVAL={};BYMONTH={}'.format(self.interval, ','.join(self.bymonth), self.bymonthdate)
                if self.bymonthdate:
                    rrule += ';BYMONTHDAY={}'.format(','.join(self.bymonthdate))
            case 'YEARDAY':
                rrule += 'FREQ=YEARLY;INTERVAL={};BYMONTH={}'.format(self.interval, ','.join(self.bymonth), self.bymonthday)
                if self.bymonthday:
                    rrule += ';BYDAY={}'.format(','.join(self.bymonthday))

        match self.repeat:
            case 'UNTIL':
                rrule += ';UNTIL={}'.format(self.until.isoformat().replace('-', '').replace(':', '')[0:15] + 'Z')
            case 'COUNT':
                rrule += ';COUNT={}'.format(self.count)
            case None:
                rrule += ';COUNT={}'.format(10000)

        return rrule

    def __str__(self):
        return self.event.summary

    class Meta:
        verbose_name = _('regra de recorrência')
        verbose_name_plural = _('regras de recorrencia')
