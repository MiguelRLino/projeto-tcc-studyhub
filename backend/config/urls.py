from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/alunos/", include("apps.alunos.urls")),
    path("api/", include("apps.sistema_estudos.urls")),
    path("api/", include("apps.cadernos.urls")),
    path("api/", include("apps.assistente_ia.urls")),
    path("api/", include("apps.telegram.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
