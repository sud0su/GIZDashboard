from django.db import models
from django.utils.translation import gettext as _

# Create your models here.
class Organization(models.Model):
    code = models.CharField(_("Organization Code"), max_length=50)
    name = models.CharField(_("Organization Name"), max_length=50)
    
    def __str__(self):
        return self.name