import os

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.cadernos.models import Caderno, ImagemCaderno, PaginaCaderno
from apps.cadernos.permissions import IsDonoCaderno, IsDonoPagina
from apps.cadernos.serializers import (
    CadernoReadSerializer,
    CadernoWriteSerializer,
    ImagemCadernoSerializer,
    MoverPaginaSerializer,
    PaginaReadSerializer,
    PaginaResumoSerializer,
    PaginaWriteSerializer,
    ReordenarPaginasSerializer,
)
from apps.cadernos.services import registrar_log_caderno
from apps.cadernos.utils import conteudo_vazio, extrair_texto_conteudo

EXTENSOES_IMAGEM = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
TAMANHO_MAX_IMAGEM = 5 * 1024 * 1024


def queryset_cadernos(aluno):
    return Caderno.objects.filter(aluno=aluno, data_exclusao__isnull=True).select_related(
        "disciplina"
    )


def queryset_paginas(aluno):
    return PaginaCaderno.objects.filter(
        caderno__aluno=aluno,
        caderno__data_exclusao__isnull=True,
        data_exclusao__isnull=True,
    ).select_related("caderno")


def obter_caderno_aluno(aluno, pk):
    return queryset_cadernos(aluno).get(pk=pk)


class CadernoListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return queryset_cadernos(self.request.user).order_by("ordem", "titulo")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CadernoWriteSerializer
        return CadernoReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = CadernoWriteSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        caderno = serializer.save()
        registrar_log_caderno(
            request.user,
            "CRIAR_CADERNO",
            f'Aluno criou o caderno "{caderno.titulo}".',
            id_registro_afetado=caderno.pk,
        )
        return Response(
            CadernoReadSerializer(caderno).data,
            status=status.HTTP_201_CREATED,
        )


class CadernoDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsDonoCaderno]
    lookup_field = "pk"

    def get_queryset(self):
        return queryset_cadernos(self.request.user)

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return CadernoWriteSerializer
        return CadernoReadSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = CadernoWriteSerializer(
            instance,
            data=request.data,
            partial=partial,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        caderno = serializer.save()
        registrar_log_caderno(
            request.user,
            "EDITAR_CADERNO",
            f'Aluno editou o caderno "{caderno.titulo}".',
            id_registro_afetado=caderno.pk,
        )
        return Response(CadernoReadSerializer(caderno).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        agora = timezone.now()
        with transaction.atomic():
            instance.data_exclusao = agora
            instance.save(update_fields=["data_exclusao"])
            instance.paginas.filter(data_exclusao__isnull=True).update(
                data_exclusao=agora
            )
        registrar_log_caderno(
            request.user,
            "EXCLUIR_CADERNO",
            f'Aluno excluiu o caderno "{instance.titulo}".',
            id_registro_afetado=instance.pk,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class PaginaListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_caderno(self):
        return obter_caderno_aluno(self.request.user, self.kwargs["pk"])

    def get_queryset(self):
        caderno = self.get_caderno()
        return caderno.paginas.filter(data_exclusao__isnull=True).order_by(
            "ordem", "titulo"
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PaginaWriteSerializer
        return PaginaResumoSerializer

    def create(self, request, *args, **kwargs):
        caderno = self.get_caderno()
        serializer = PaginaWriteSerializer(
            data=request.data,
            context={"request": request, "caderno": caderno},
        )
        serializer.is_valid(raise_exception=True)
        pagina = serializer.save()
        registrar_log_caderno(
            request.user,
            "CRIAR_PAGINA",
            f'Aluno criou a página "{pagina.titulo}" no caderno "{caderno.titulo}".',
            tabela_afetada="pagina_caderno",
            id_registro_afetado=pagina.pk,
        )
        return Response(
            PaginaReadSerializer(pagina).data,
            status=status.HTTP_201_CREATED,
        )


class PaginaDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsDonoPagina]
    lookup_field = "pk"

    def get_queryset(self):
        return queryset_paginas(self.request.user)

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return PaginaWriteSerializer
        return PaginaReadSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = PaginaWriteSerializer(
            instance,
            data=request.data,
            partial=partial,
            context={"request": request, "caderno": instance.caderno},
        )
        serializer.is_valid(raise_exception=True)
        pagina = serializer.save()
        registrar_log_caderno(
            request.user,
            "EDITAR_PAGINA",
            f'Aluno editou a página "{pagina.titulo}" do caderno "{pagina.caderno.titulo}".',
            tabela_afetada="pagina_caderno",
            id_registro_afetado=pagina.pk,
        )
        return Response(PaginaReadSerializer(pagina).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.data_exclusao = timezone.now()
        instance.save(update_fields=["data_exclusao"])
        registrar_log_caderno(
            request.user,
            "EXCLUIR_PAGINA",
            f'Aluno excluiu a página "{instance.titulo}" do caderno "{instance.caderno.titulo}".',
            tabela_afetada="pagina_caderno",
            id_registro_afetado=instance.pk,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class PaginaDuplicarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        pagina = queryset_paginas(request.user).get(pk=pk)
        ultima = (
            pagina.caderno.paginas.filter(data_exclusao__isnull=True)
            .order_by("-ordem")
            .values_list("ordem", flat=True)
            .first()
        )
        nova = PaginaCaderno.objects.create(
            caderno=pagina.caderno,
            titulo=f"{pagina.titulo} (cópia)"[:200],
            conteudo=pagina.conteudo,
            ordem=(ultima or 0) + 1,
            favorita=False,
            quantidade_palavras=pagina.quantidade_palavras,
            quantidade_caracteres=pagina.quantidade_caracteres,
        )
        registrar_log_caderno(
            request.user,
            "DUPLICAR_PAGINA",
            f'Aluno duplicou a página "{pagina.titulo}" do caderno "{pagina.caderno.titulo}".',
            tabela_afetada="pagina_caderno",
            id_registro_afetado=nova.pk,
        )
        return Response(PaginaReadSerializer(nova).data, status=status.HTTP_201_CREATED)


class PaginaMoverAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        pagina = queryset_paginas(request.user).get(pk=pk)
        serializer = MoverPaginaSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        destino = obter_caderno_aluno(
            request.user, serializer.validated_data["caderno_destino_id"]
        )
        origem_titulo = pagina.caderno.titulo
        ultima = (
            destino.paginas.filter(data_exclusao__isnull=True)
            .order_by("-ordem")
            .values_list("ordem", flat=True)
            .first()
        )
        pagina.caderno = destino
        pagina.ordem = (ultima or 0) + 1
        pagina.save(update_fields=["caderno", "ordem", "data_atualizacao"])
        registrar_log_caderno(
            request.user,
            "MOVER_PAGINA",
            f'Aluno moveu a página "{pagina.titulo}" de "{origem_titulo}" para "{destino.titulo}".',
            tabela_afetada="pagina_caderno",
            id_registro_afetado=pagina.pk,
        )
        return Response(PaginaReadSerializer(pagina).data)


class PaginaFavoritarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        pagina = queryset_paginas(request.user).get(pk=pk)
        favorita = request.data.get("favorita")
        if favorita is None:
            pagina.favorita = not pagina.favorita
        else:
            pagina.favorita = bool(favorita)
        pagina.save(update_fields=["favorita", "data_atualizacao"])
        acao = "FAVORITAR_PAGINA" if pagina.favorita else "DESFAVORITAR_PAGINA"
        registrar_log_caderno(
            request.user,
            acao,
            f'Aluno alterou favorito da página "{pagina.titulo}".',
            tabela_afetada="pagina_caderno",
            id_registro_afetado=pagina.pk,
        )
        return Response(PaginaReadSerializer(pagina).data)


class PaginaPesquisarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        q = (request.query_params.get("q") or "").strip()
        qs = queryset_paginas(request.user)
        if q:
            ids = []
            base_ids = list(qs.values_list("pk", flat=True))
            for pagina in PaginaCaderno.objects.filter(pk__in=base_ids).only(
                "pk", "titulo", "conteudo"
            ):
                texto = extrair_texto_conteudo(pagina.conteudo)
                if q.lower() in pagina.titulo.lower() or q.lower() in texto.lower():
                    ids.append(pagina.pk)
            qs = qs.filter(pk__in=ids) if ids else qs.none()
        favoritas = request.query_params.get("favoritas")
        if favoritas in ("1", "true", "True"):
            qs = qs.filter(favorita=True)
        qs = qs.order_by("-data_atualizacao")[:50]
        return Response(PaginaResumoSerializer(qs, many=True).data)


class PaginaReordenarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        caderno = obter_caderno_aluno(request.user, pk)
        serializer = ReordenarPaginasSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mapa = {
            int(item["id_pagina"]): int(item["ordem"])
            for item in serializer.validated_data["ordens"]
        }
        paginas = list(
            caderno.paginas.filter(data_exclusao__isnull=True, pk__in=mapa.keys())
        )
        for pagina in paginas:
            pagina.ordem = mapa[pagina.pk]
        PaginaCaderno.objects.bulk_update(paginas, ["ordem"])
        return Response({"ok": True})


class PaginaExportarPdfAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        pagina = queryset_paginas(request.user).get(pk=pk)
        registrar_log_caderno(
            request.user,
            "EXPORTAR_PDF",
            f'Aluno exportou a página "{pagina.titulo}" do caderno "{pagina.caderno.titulo}" em PDF.',
            tabela_afetada="pagina_caderno",
            id_registro_afetado=pagina.pk,
        )
        return Response({"ok": True})


class ImagemUploadAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        pagina = queryset_paginas(request.user).get(pk=pk)
        arquivo = request.FILES.get("arquivo")
        if not arquivo:
            return Response(
                {"erro": "Envie um arquivo de imagem."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ext = os.path.splitext(arquivo.name)[1].lower()
        if ext not in EXTENSOES_IMAGEM:
            return Response(
                {"erro": "Formato não permitido. Use JPG, PNG, GIF ou WEBP."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if arquivo.size > TAMANHO_MAX_IMAGEM:
            return Response(
                {"erro": "Imagem acima do limite de 5 MB."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        imagem = ImagemCaderno.objects.create(
            pagina=pagina,
            arquivo=arquivo,
            nome_original=arquivo.name[:255],
        )
        return Response(
            ImagemCadernoSerializer(imagem, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class CadernoPesquisarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        q = (request.query_params.get("q") or "").strip()
        qs = queryset_cadernos(request.user)
        if q:
            qs = qs.filter(Q(titulo__icontains=q) | Q(descricao__icontains=q))
        return Response(CadernoReadSerializer(qs.order_by("ordem", "titulo"), many=True).data)
