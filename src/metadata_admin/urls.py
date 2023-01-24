from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import include, path
from django.views.generic.base import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('', admin.site.urls),
    path(
        'docs/',
        SpectacularSwaggerView.as_view(
            template_name='../../templates/swagger-ui.html',
            url_name='schema',
        ),
        name='swagger-ui',
    )
]
