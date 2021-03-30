from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url, include

from .views import home, upload, display

app_name = 'captchaimages'
urlpatterns = [
    path('', home, name='home'),
    path('display/', display, name="display"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)