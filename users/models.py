from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

#these are model abstracts from django extensions
from django_extensions.db.models import (
    TimeStampedModel,
	ActivatorModel 
)

class UserProfile(TimeStampedModel,ActivatorModel,models.Model):
    '''
    Our UserProfile model extends the built-in Django User Model
    This is specific to the user! i.e. the individual that signs up
    '''
    class Meta:
        verbose_name_plural = 'User profiles'
        ordering = ["id"]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telephone = models.CharField(verbose_name="Contact telephone number", max_length=255, null=True, blank=True)
    address = models.CharField(verbose_name="Address",max_length=100, null=True, blank=True)
    town = models.CharField(verbose_name="Town/City",max_length=100, null=True, blank=True)
    county = models.CharField(verbose_name="County",max_length=100, null=True, blank=True)
    post_code = models.CharField(verbose_name="Zip/Post Code",max_length=8, null=True, blank=True)
    country = models.CharField(verbose_name="Country",max_length=100, null=True, blank=True)
    longitude = models.CharField(verbose_name="Longitude",max_length=50, null=True, blank=True)
    latitude = models.CharField(verbose_name="Latitude",max_length=50, null=True, blank=True)

    avatar = models.ImageField(default='default_avatar.jpg', upload_to='avatar', null=True, blank=True)
	
    def __str__(self):
        if self.user.first_name and self.user.last_name:
            return f'{self.user.first_name} {self.user.last_name}'
        return self.user.email

