"""Integração com Telegram Bot API."""

import logging
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}/{method}"


class TelegramServiceError(Exception):
    """Erro ao comunicar com a Telegram API."""


class TelegramService:
    @staticmethod
    def _token() -> str:
        token = getattr(settings, "TELEGRAM_BOT_TOKEN", "").strip()
        if not token:
            raise TelegramServiceError("Bot do Telegram não configurado.")
        return token

    @classmethod
    def _request(cls, method: str, payload: dict | None = None) -> dict:
        url = TELEGRAM_API_BASE.format(token=cls._token(), method=method)
        try:
            response = requests.post(url, json=payload or {}, timeout=15)
            data = response.json()
        except requests.RequestException as exc:
            logger.exception("Falha HTTP Telegram (%s)", method)
            raise TelegramServiceError("Falha na comunicação com o Telegram.") from exc
        except ValueError as exc:
            raise TelegramServiceError("Resposta inválida do Telegram.") from exc

        if not data.get("ok"):
            desc = (data.get("description") or "Erro desconhecido")[:200]
            logger.error("Telegram API %s falhou: %s", method, desc)
            raise TelegramServiceError(desc)
        return data

    @classmethod
    def enviar_mensagem(cls, chat_id: int | str, mensagem: str) -> dict:
        if not chat_id:
            raise TelegramServiceError("Chat ID inválido.")
        texto = (mensagem or "").strip()
        if not texto:
            raise TelegramServiceError("Mensagem vazia.")
        return cls._request(
            "sendMessage",
            {"chat_id": chat_id, "text": texto[:4096]},
        )

    @classmethod
    def obter_updates(cls, offset: int | None = None, timeout: int = 30) -> list[dict]:
        payload: dict[str, Any] = {"timeout": timeout}
        if offset is not None:
            payload["offset"] = offset
        url = TELEGRAM_API_BASE.format(token=cls._token(), method="getUpdates")
        try:
            response = requests.get(url, params=payload, timeout=timeout + 5)
            data = response.json()
        except requests.RequestException as exc:
            logger.exception("Falha ao obter updates do Telegram")
            raise TelegramServiceError("Falha ao obter updates.") from exc
        if not data.get("ok"):
            desc = (data.get("description") or "Erro")[:200]
            raise TelegramServiceError(desc)
        return data.get("result") or []
