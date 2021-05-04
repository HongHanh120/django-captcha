from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt

from .views import *

app_name = 'captchaimages'
urlpatterns = [
    path('', csrf_exempt(home), name='home'),
    path('display-image/', display_image, name='display'),
    path('send-answer/', csrf_exempt(TemplateView.as_view(template_name='includes/captcha_image.html')), name='submit'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
