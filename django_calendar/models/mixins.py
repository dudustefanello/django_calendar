from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.utils.translation import gettext_lazy as _


def get_site_id():
    return settings.SITE_ID


class SiteMixin(models.Model):
    site = models.ForeignKey(to=Site, on_delete=models.PROTECT, editable=False, default=get_site_id,
                             verbose_name=_('site'))

    objects = CurrentSiteManager()

    class Meta:
        abstract = True


class BaseModel(SiteMixin):
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('criado em'))
    modified = models.DateTimeField(auto_now=True, verbose_name=_('modificado em'))

    class BaseMeta:
        get_latest_by = 'created'

    class Meta(BaseMeta):
        abstract = True


class SummaryMixin(models.Model):
    summary = models.CharField(max_length=255, verbose_name=_('descrição'))

    def __str__(self):
        return self.summary

    class Meta:
        abstract = True


class DescriptionMixin(models.Model):
    description = models.TextField(null=True, blank=True, verbose_name=_('detalhes'))

    class Meta:
        abstract = True
