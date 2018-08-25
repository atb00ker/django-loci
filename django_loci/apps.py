from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class LociConfig(AppConfig):
    name = 'django_loci'
    verbose_name = _('django-loci')

    def __setmodels__(self):
        """
        this method can be overridden in 3rd party apps
        """
        from .models import Location
        self.location_model = Location

    def ready(self):
        import leaflet
        leaflet.app_settings['NO_GLOBALS'] = False
        self.__setmodels__()
