"""Feriados nacionais brasileiros via Brasil API (com fallback local)."""

from __future__ import annotations

import calendar
from datetime import date, timedelta

import requests

_CACHE: dict[int, list[dict]] = {}


def _feriados_fixos(ano: int) -> list[dict]:
    """Feriados nacionais fixos (fallback se a API externa falhar)."""
    fixos = [
        (1, 1, "Confraternização Universal"),
        (4, 21, "Tiradentes"),
        (5, 1, "Dia do Trabalho"),
        (9, 7, "Independência do Brasil"),
        (10, 12, "Nossa Senhora Aparecida"),
        (11, 2, "Finados"),
        (11, 15, "Proclamação da República"),
        (12, 25, "Natal"),
    ]
    return [
        {"data": date(ano, mes, dia).isoformat(), "nome": nome, "tipo": "nacional"}
        for mes, dia, nome in fixos
    ]


def _pascoa(ano: int) -> date:
    """Algoritmo de Meeus/Jones/Butcher para domingo de Páscoa."""
    a = ano % 19
    b = ano // 100
    c = ano % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return date(ano, mes, dia)


def _feriados_moveis(ano: int) -> list[dict]:
    pascoa = _pascoa(ano)
    moveis = [
        (pascoa - timedelta(days=48), "Segunda-feira de Carnaval"),
        (pascoa - timedelta(days=47), "Terça-feira de Carnaval"),
        (pascoa - timedelta(days=2), "Sexta-feira Santa"),
        (pascoa, "Páscoa"),
        (pascoa + timedelta(days=60), "Corpus Christi"),
    ]
    return [
        {"data": d.isoformat(), "nome": nome, "tipo": "nacional"} for d, nome in moveis
    ]


def listar_feriados_ano(ano: int) -> list[dict]:
    if ano in _CACHE:
        return _CACHE[ano]

    feriados: list[dict] = []
    try:
        resp = requests.get(
            f"https://brasilapi.com.br/api/feriados/v1/{ano}",
            timeout=5,
        )
        resp.raise_for_status()
        for item in resp.json():
            feriados.append(
                {
                    "data": item["date"],
                    "nome": item["name"],
                    "tipo": item.get("type", "nacional"),
                }
            )
    except Exception:
        feriados = _feriados_fixos(ano) + _feriados_moveis(ano)

    feriados.sort(key=lambda f: f["data"])
    _CACHE[ano] = feriados
    return feriados


def listar_feriados_mes(ano: int, mes: int) -> list[dict]:
    prefixo = f"{ano}-{mes:02d}-"
    return [f for f in listar_feriados_ano(ano) if f["data"].startswith(prefixo)]


def intervalo_mes(ano: int, mes: int) -> tuple[date, date]:
    ultimo = calendar.monthrange(ano, mes)[1]
    return date(ano, mes, 1), date(ano, mes, ultimo)
