from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 2200, 1600
BOX_W = 280
HEADER_H = 32
ROW_H = 22
PAD = 8

img = Image.new("RGB", (W, H), "#FFFFFF")
draw = ImageDraw.Draw(img)

try:
    font_title = ImageFont.truetype("arialbd.ttf", 18)
    font = ImageFont.truetype("arial.ttf", 14)
    font_small = ImageFont.truetype("arial.ttf", 12)
    font_header = ImageFont.truetype("arialbd.ttf", 28)
except OSError:
    font_title = ImageFont.load_default()
    font = font_title
    font_small = font_title
    font_header = font_title

tables = {
    "aluno": {
        "pos": (80, 80),
        "fields": [
            ("PK", "id_aluno INT"),
            ("", "nome VARCHAR(100)"),
            ("", "email VARCHAR(150)"),
            ("", "senha VARCHAR(255)"),
        ],
    },
    "disciplina": {
        "pos": (480, 80),
        "fields": [
            ("PK", "id_disciplina INT"),
            ("FK", "aluno_id_aluno INT"),
            ("", "nome VARCHAR(100)"),
            ("", "nivel_dificuldade INT"),
            ("", "data_exclusao DATETIME"),
        ],
    },
    "tarefa": {
        "pos": (880, 80),
        "fields": [
            ("PK", "id_tarefa INT"),
            ("FK", "disciplina_id_disciplina INT"),
            ("", "descricao VARCHAR(255)"),
            ("", "data_entrega DATE"),
            ("", "hora_entrega TIME"),
            ("", "status_tarefa VARCHAR(20)"),
            ("", "data_exclusao DATETIME"),
        ],
    },
    "sessao_estudo": {
        "pos": (480, 360),
        "fields": [
            ("PK", "id_sessao_estudo INT"),
            ("FK", "aluno_id_aluno INT"),
            ("FK", "disciplina_id_disciplina INT"),
            ("", "tempo_estudo DECIMAL(5,2)"),
            ("", "data_sessao DATE"),
            ("", "nivel_dificuldade INT"),
            ("", "data_exclusao DATETIME"),
        ],
    },
    "sessao_planejada": {
        "pos": (880, 360),
        "fields": [
            ("PK", "id_sessao_planejada INT"),
            ("FK", "aluno_id_aluno INT"),
            ("FK", "disciplina_id_disciplina INT"),
            ("", "data_planejada DATE"),
            ("", "duracao_prevista_minutos INT"),
            ("", "observacao VARCHAR(255)"),
            ("", "data_exclusao DATETIME"),
        ],
    },
    "caderno": {
        "pos": (1280, 80),
        "fields": [
            ("PK", "id_caderno INT"),
            ("FK", "aluno_id_aluno INT"),
            ("FK", "disciplina_id_disciplina INT"),
            ("", "titulo VARCHAR(150)"),
            ("", "descricao VARCHAR(500)"),
            ("", "cor VARCHAR(20)"),
            ("", "ordem INT"),
            ("", "data_exclusao DATETIME"),
        ],
    },
    "pagina_caderno": {
        "pos": (1680, 80),
        "fields": [
            ("PK", "id_pagina INT"),
            ("FK", "caderno_id_caderno INT"),
            ("", "titulo VARCHAR(200)"),
            ("", "conteudo JSON"),
            ("", "ordem INT"),
            ("", "favorita BOOLEAN"),
            ("", "quantidade_palavras INT"),
            ("", "data_exclusao DATETIME"),
        ],
    },
    "imagem_caderno": {
        "pos": (1680, 420),
        "fields": [
            ("PK", "id_imagem INT"),
            ("FK", "pagina_id_pagina INT"),
            ("", "arquivo VARCHAR(255)"),
            ("", "nome_original VARCHAR(255)"),
            ("", "data_upload DATETIME"),
            ("", "data_exclusao DATETIME"),
        ],
    },
    "conversa_ia": {
        "pos": (80, 420),
        "fields": [
            ("PK", "id_conversa INT"),
            ("FK", "aluno_id_aluno INT"),
            ("", "pergunta TEXT"),
            ("", "resposta TEXT"),
            ("", "data_criacao DATETIME"),
            ("", "data_exclusao DATETIME"),
        ],
    },
    "configuracao_telegram": {
        "pos": (80, 760),
        "fields": [
            ("PK", "id_configuracao INT"),
            ("FK", "aluno_id_aluno INT"),
            ("", "telegram_chat_id BIGINT"),
            ("", "telegram_username VARCHAR(100)"),
            ("", "telegram_ativo BOOLEAN"),
            ("", "notificar_24h BOOLEAN"),
            ("", "notificar_2h BOOLEAN"),
            ("", "data_conexao DATETIME"),
        ],
    },
    "notificacao_telegram": {
        "pos": (480, 760),
        "fields": [
            ("PK", "id_notificacao INT"),
            ("FK", "aluno_id_aluno INT"),
            ("FK", "tarefa_id_tarefa INT"),
            ("", "tipo VARCHAR(20)"),
            ("", "status_envio VARCHAR(20)"),
            ("", "data_envio DATETIME"),
            ("", "erro VARCHAR(255)"),
        ],
    },
    "codigo_conexao_telegram": {
        "pos": (880, 760),
        "fields": [
            ("PK", "id_codigo INT"),
            ("FK", "aluno_id_aluno INT"),
            ("", "codigo VARCHAR(10)"),
            ("", "data_criacao DATETIME"),
            ("", "data_expiracao DATETIME"),
            ("", "utilizado BOOLEAN"),
        ],
    },
    "relatorio": {
        "pos": (1280, 520),
        "fields": [
            ("PK", "id_relatorio INT"),
            ("FK", "aluno_id_aluno INT"),
            ("", "periodo VARCHAR(50)"),
            ("", "total_horas DECIMAL(5,2)"),
            ("", "data_exclusao DATETIME"),
        ],
    },
}

rels = [
    ("aluno", "disciplina", "1", "N"),
    ("disciplina", "tarefa", "1", "N"),
    ("aluno", "sessao_estudo", "1", "N"),
    ("disciplina", "sessao_estudo", "1", "N"),
    ("aluno", "sessao_planejada", "1", "N"),
    ("disciplina", "sessao_planejada", "1", "N"),
    ("aluno", "caderno", "1", "N"),
    ("disciplina", "caderno", "0..1", "N"),
    ("caderno", "pagina_caderno", "1", "N"),
    ("pagina_caderno", "imagem_caderno", "1", "N"),
    ("aluno", "conversa_ia", "1", "N"),
    ("aluno", "configuracao_telegram", "1", "0..1"),
    ("aluno", "codigo_conexao_telegram", "1", "N"),
    ("aluno", "notificacao_telegram", "1", "N"),
    ("tarefa", "notificacao_telegram", "1", "N"),
    ("aluno", "relatorio", "1", "N"),
]


def box_size(fields):
    h = HEADER_H + len(fields) * ROW_H + PAD
    return BOX_W, h


def box_rect(name):
    x, y = tables[name]["pos"]
    w, h = box_size(tables[name]["fields"])
    return x, y, x + w, y + h


def center(name):
    x1, y1, x2, y2 = box_rect(name)
    return (x1 + x2) // 2, (y1 + y2) // 2


def edge_point(name, toward):
    x1, y1, x2, y2 = box_rect(name)
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    tx, ty = toward
    dx, dy = tx - cx, ty - cy
    if abs(dx) >= abs(dy):
        return (x2, cy) if dx >= 0 else (x1, cy)
    return (cx, y2) if dy >= 0 else (cx, y1)


draw.text((80, 20), "Modelagem Relacional - StudyHub", fill="#111827", font=font_header)

for a, b, c_a, c_b in rels:
    ca = center(a)
    cb = center(b)
    p1 = edge_point(a, cb)
    p2 = edge_point(b, ca)
    draw.line([p1, p2], fill="#64748B", width=2)
    mx = int(p1[0] * 0.75 + p2[0] * 0.25)
    my = int(p1[1] * 0.75 + p2[1] * 0.25)
    nx = int(p1[0] * 0.25 + p2[0] * 0.75)
    ny = int(p1[1] * 0.25 + p2[1] * 0.75)
    draw.text((mx + 4, my - 14), c_a, fill="#0F766E", font=font_small)
    draw.text((nx + 4, ny - 14), c_b, fill="#0F766E", font=font_small)

for name, meta in tables.items():
    x, y = meta["pos"]
    fields = meta["fields"]
    w, h = box_size(fields)
    draw.rounded_rectangle([x + 3, y + 3, x + w + 3, y + h + 3], radius=6, fill="#E5E7EB")
    draw.rounded_rectangle(
        [x, y, x + w, y + h], radius=6, fill="#FFFFFF", outline="#1F2937", width=2
    )
    draw.rounded_rectangle([x, y, x + w, y + HEADER_H], radius=6, fill="#0F766E", outline="#0F766E")
    draw.rectangle([x, y + HEADER_H - 8, x + w, y + HEADER_H], fill="#0F766E")
    draw.text((x + 10, y + 7), name, fill="#FFFFFF", font=font_title)

    yy = y + HEADER_H + 4
    for kind, text in fields:
        if kind == "PK":
            prefix = "[PK] "
            color = "#B45309"
        elif kind == "FK":
            prefix = "[FK] "
            color = "#1D4ED8"
        else:
            prefix = "     "
            color = "#111827"
        draw.text((x + 8, yy), f"{prefix}{text}", fill=color, font=font)
        yy += ROW_H

lx, ly = 1280, 900
draw.rounded_rectangle(
    [lx, ly, lx + 520, ly + 160], radius=8, fill="#F8FAFC", outline="#CBD5E1", width=2
)
draw.text((lx + 16, ly + 12), "Legenda", fill="#111827", font=font_title)
draw.text((lx + 16, ly + 48), "[PK]  Chave Primaria", fill="#B45309", font=font)
draw.text((lx + 16, ly + 76), "[FK]  Chave Estrangeira", fill="#1D4ED8", font=font)
draw.text(
    (lx + 16, ly + 104),
    "1 / N / 0..1  Cardinalidade do relacionamento",
    fill="#334155",
    font=font,
)
draw.text((lx + 16, ly + 132), "Banco MySQL — StudyHub", fill="#64748B", font=font_small)

out = Path(__file__).resolve().parent / "modelagem-dados-studyhub.png"
img.save(out, "PNG")
print(f"saved {out} ({out.stat().st_size} bytes)")
