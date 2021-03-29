from django.db import models


# Create your models here.
class Image(models.Model):
    text = models.CharField(blank=False, max_length=32, default='CAPTCHA')
    image = models.ImageField(upload_to='images/', blank=True)

    def __str__(self):
        return self.text
