from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """Respostas JSON mais consistentes para erros da API."""
    response = exception_handler(exc, context)
    if response is not None:
        detail = response.data
        if isinstance(detail, dict) and len(detail) == 1 and "detail" in detail:
            response.data = {"erro": detail["detail"]}
        elif isinstance(detail, dict):
            response.data = {"erros": detail}
        else:
            response.data = {"erro": detail}
    return response
