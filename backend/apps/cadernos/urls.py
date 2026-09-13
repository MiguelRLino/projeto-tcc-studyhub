from django.urls import path

from apps.cadernos.views import (
    CadernoDetailAPIView,
    CadernoListCreateAPIView,
    CadernoPesquisarAPIView,
    ImagemUploadAPIView,
    PaginaDetailAPIView,
    PaginaDuplicarAPIView,
    PaginaExportarPdfAPIView,
    PaginaFavoritarAPIView,
    PaginaListCreateAPIView,
    PaginaMoverAPIView,
    PaginaPesquisarAPIView,
    PaginaReordenarAPIView,
)

urlpatterns = [
    path("cadernos/", CadernoListCreateAPIView.as_view(), name="caderno-list-create"),
    path("cadernos/pesquisar/", CadernoPesquisarAPIView.as_view(), name="caderno-pesquisar"),
    path("cadernos/<int:pk>/", CadernoDetailAPIView.as_view(), name="caderno-detail"),
    path(
        "cadernos/<int:pk>/paginas/",
        PaginaListCreateAPIView.as_view(),
        name="caderno-paginas",
    ),
    path(
        "cadernos/<int:pk>/paginas/reordenar/",
        PaginaReordenarAPIView.as_view(),
        name="caderno-paginas-reordenar",
    ),
    path("paginas/pesquisar/", PaginaPesquisarAPIView.as_view(), name="pagina-pesquisar"),
    path("paginas/<int:pk>/", PaginaDetailAPIView.as_view(), name="pagina-detail"),
    path(
        "paginas/<int:pk>/duplicar/",
        PaginaDuplicarAPIView.as_view(),
        name="pagina-duplicar",
    ),
    path(
        "paginas/<int:pk>/mover/",
        PaginaMoverAPIView.as_view(),
        name="pagina-mover",
    ),
    path(
        "paginas/<int:pk>/favoritar/",
        PaginaFavoritarAPIView.as_view(),
        name="pagina-favoritar",
    ),
    path(
        "paginas/<int:pk>/exportar-pdf/",
        PaginaExportarPdfAPIView.as_view(),
        name="pagina-exportar-pdf",
    ),
    path(
        "paginas/<int:pk>/imagens/",
        ImagemUploadAPIView.as_view(),
        name="pagina-imagem-upload",
    ),
]
