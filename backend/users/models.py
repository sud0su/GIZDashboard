import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _

# Create your models here.
class Profile(AbstractUser):
    birthday = models.DateField(_('Birthday'), default=datetime.date.today)
    genderlist = (
        (1, 'Man'),
        (2, 'Woman'),
    )
    gender = models.IntegerField(_('Gender'), null=True, blank=True, choices=genderlist, default=1)
    profile = models.TextField(_('Profile'), null=True, blank=True)

    def __str__(self):
        return self.email