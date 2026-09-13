"""Utilitários do Caderno Digital."""

import re
from typing import Any


def conteudo_vazio() -> dict:
    return {"type": "doc", "content": [{"type": "paragraph"}]}


def normalizar_conteudo(conteudo: Any) -> dict:
    if isinstance(conteudo, dict) and conteudo.get("type") == "doc":
        return conteudo
    return conteudo_vazio()


def extrair_texto_conteudo(conteudo: Any) -> str:
    """Extrai texto plano do JSON do Tiptap para busca e contadores."""

    partes: list[str] = []

    def walk(node):
        if not isinstance(node, dict):
            return
        if node.get("type") == "text":
            partes.append(str(node.get("text", "")))
        for child in node.get("content") or []:
            walk(child)

    walk(normalizar_conteudo(conteudo))
    return " ".join(p.strip() for p in partes if p.strip())


def calcular_metricas_texto(texto: str) -> tuple[int, int]:
    limpo = (texto or "").strip()
    if not limpo:
        return 0, 0
    caracteres = len(limpo)
    palavras = len(re.findall(r"\S+", limpo))
    return palavras, caracteres


def calcular_metricas_conteudo(conteudo: Any) -> tuple[int, int]:
    return calcular_metricas_texto(extrair_texto_conteudo(conteudo))


def tempo_leitura_minutos(palavras: int, palavras_por_minuto: int = 200) -> int:
    if palavras <= 0:
        return 0
    return max(1, round(palavras / palavras_por_minuto))
