from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _

class MoneyManagerAdminSite(AdminSite):
    # Personalización del sitio de administración
    site_title = _('Money Manager Admin')
    site_header = _('Money Manager')
    index_title = _('Panel de Control')

# Crear una instancia personalizada del sitio de administración
money_manager_admin = MoneyManagerAdminSite(name='money_manager_admin') 