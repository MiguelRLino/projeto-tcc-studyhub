from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/alunos/", include("apps.alunos.urls")),
    path("api/", include("apps.sistema_estudos.urls")),
]
