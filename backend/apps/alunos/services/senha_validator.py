"""Regras de complexidade de senha do StudyHub."""

import re

RE_MAIUSCULA = re.compile(r"[A-Z]")
RE_NUMERO = re.compile(r"\d")
RE_ESPECIAL = re.compile(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;'/`~]")


def validar_senha_forte(senha: str) -> list[str]:
    """
    Retorna lista de mensagens de erro (vazia se a senha atende todas as regras).
    """
    erros: list[str] = []
    if senha is None:
        return ["Senha é obrigatória."]
    if len(senha) < 8:
        erros.append("A senha deve ter no mínimo 8 caracteres.")
    if not RE_MAIUSCULA.search(senha):
        erros.append("A senha deve conter pelo menos uma letra maiúscula.")
    if not RE_NUMERO.search(senha):
        erros.append("A senha deve conter pelo menos um número.")
    if not RE_ESPECIAL.search(senha):
        erros.append("A senha deve conter pelo menos um caractere especial.")
    return erros


def mensagem_erro_senha(senha: str) -> str | None:
    erros = validar_senha_forte(senha)
    if not erros:
        return None
    return " ".join(erros)
