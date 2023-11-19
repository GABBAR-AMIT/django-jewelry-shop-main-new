
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
# from webs.views import catandcolor

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
    path('adminlogin/', include('webb.urls')),
    # path('/test/', catandcolor),
]

# To display images
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

