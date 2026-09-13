from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assistente_ia.models import ConversaIA
from apps.assistente_ia.serializers import ConversaReadSerializer, PerguntaSerializer
from apps.assistente_ia.services import (
    GeminiConfigError,
    GeminiIndisponivelError,
    LimiteUsoAtingidoError,
    processar_pergunta,
)


def queryset_conversas(aluno):
    return ConversaIA.objects.filter(
        aluno=aluno,
        data_exclusao__isnull=True,
    )


class AssistentePerguntarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PerguntaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            conversa = processar_pergunta(
                request.user,
                serializer.validated_data["pergunta"],
            )
        except LimiteUsoAtingidoError as exc:
            return Response({"erro": str(exc)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except ValueError as exc:
            return Response({"erro": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except GeminiConfigError:
            return Response(
                {"erro": "Não foi possível processar sua pergunta."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except GeminiIndisponivelError:
            return Response(
                {"erro": "Não foi possível processar sua pergunta."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except Exception:
            return Response(
                {"erro": "Não foi possível processar sua pergunta."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response({"resposta": conversa.resposta})


class AssistenteHistoricoListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = queryset_conversas(request.user).order_by("-data_criacao")[:100]
        return Response(ConversaReadSerializer(qs, many=True).data)


class AssistenteHistoricoDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        conversa = queryset_conversas(request.user).filter(pk=pk).first()
        if not conversa:
            return Response(
                {"erro": "Conversa não encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(ConversaReadSerializer(conversa).data)

    def delete(self, request, pk):
        conversa = queryset_conversas(request.user).filter(pk=pk).first()
        if not conversa:
            return Response(
                {"erro": "Conversa não encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )
        conversa.data_exclusao = timezone.now()
        conversa.save(update_fields=["data_exclusao"])
        return Response(status=status.HTTP_204_NO_CONTENT)
