import uuid

from dateutil import rrule
from django.db import models
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField

from django_calendar.models.managers import EventManager, RecurrencyRuleManager
from django_calendar.models.mixins import BaseModel, DescriptionMixin, SiteMixin, SummaryMixin


class Status(BaseModel, SummaryMixin):
    class Meta(BaseModel.BaseMeta):
        verbose_name = _('situação')
        verbose_name_plural = _('situações')


class Calendar(BaseModel, SummaryMixin):
    uid = models.UUIDField(default=uuid.uuid4, unique=True, auto_created=True, editable=False,
                           verbose_name=_('id único'))

    class Meta(BaseModel.BaseMeta):
        verbose_name = _('calandário')
        verbose_name_plural = _('calendários')


class Event(BaseModel, SummaryMixin, DescriptionMixin):
    calendar = models.ForeignKey(to='calendar.Calendar', on_delete=models.CASCADE, verbose_name=_('calendário'))
    uid = models.UUIDField(default=uuid.uuid4, auto_created=True, editable=False, verbose_name=_('id único'))
    dtstart = models.DateTimeField(verbose_name=_('data e hora inicial'))
    dtend = models.DateTimeField(verbose_name=_('data e hora final'))
    status = models.ForeignKey(to='calendar.Status', on_delete=models.DO_NOTHING)
    sequence = models.PositiveSmallIntegerField(default=0, verbose_name=_('versão'))

    objects = EventManager()

    def get_object(self, data):
        return {
            'calendar': self.calendar,
            'uid': self.uid,
            'dtstart': self.dtstart.replace(year=data.year, month=data.month, day=data.day),
            'dtend': self.dtend.replace(year=data.year, month=data.month, day=data.day),
            'status': self.status,
            'sequence': self.sequence,
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
    freq = models.CharField(max_length=7, choices=[
        ('DAILY', _('Diária')),
        ('WEEKLY', _('Semanal')),
        ('MONTHLY', _('Mensal')),
        ('YEARLY', _('Anual')),
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
    byweek = models.CharField(
        max_length=20, null=True, blank=True, verbose_name=_('semana'), editable=False,
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
    bymonthday = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_('dia do mês'))

    objects = RecurrencyRuleManager()

    def get_freq(self):
        if self.freq == 'DAILY': return rrule.DAILY
        if self.freq == 'WEEKLY': return rrule.WEEKLY
        if self.freq == 'MONTHLY': return rrule.MONTHLY
        if self.freq == 'YEARLY': return rrule.YEARLY

    def get_byday(self):
        byday = []
        if 'SU' in self.byday: byday.append(rrule.SU)
        if 'MO' in self.byday: byday.append(rrule.MO)
        if 'TU' in self.byday: byday.append(rrule.TU)
        if 'WE' in self.byday: byday.append(rrule.WE)
        if 'TH' in self.byday: byday.append(rrule.TH)
        if 'FR' in self.byday: byday.append(rrule.FR)
        if 'SA' in self.byday: byday.append(rrule.SA)
        return byday

    def get_byweek(self):
        if not self.byweek:
            return None
        byweek = []
        bw = self.byweek.split(',')
        if '1' in bw: byweek.append(1)
        if '2' in bw: byweek.append(2)
        if '3' in bw: byweek.append(3)
        if '4' in bw: byweek.append(4)
        if '5' in bw: byweek.append(5)
        if '-1' in bw: byweek.append(-1)
        return byweek

    def get_datetimes(self, until=None):
        return rrule.rrule(
            freq=self.get_freq(),
            dtstart=self.event.dtstart,
            interval=self.interval,
            count=self.count if self.count else 3650,
            until=self.until if self.until else until,
            bymonth=self.bymonth,
            bymonthday=self.bymonthday,
            byweekday=self.get_byday(),
            bysetpos=self.get_byweek(),
        )

    def __str__(self):
        return self.event.summary

    class Meta:
        verbose_name = _('regra de recorrência')
        verbose_name_plural = _('regras de recorrencia')
