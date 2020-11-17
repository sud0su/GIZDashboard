from django.db import models
from django.utils.translation import gettext as _

# Create your models here.
class Organization(models.Model):
    code = models.CharField(_("Organization Code"), max_length=50)
    name = models.CharField(_("Organization Name"), max_length=50, null=True, blank=True)
    
    def __str__(self):
        if self.name == 'Null' or self.name == None:
            return self.code
        return self.name