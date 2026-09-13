---
name: avaliacao-seguranca-studyhub
description: >-
  Avalia aspectos de segurança do sistema StudyHub (Django REST + React + MySQL)
  e gera relatório Markdown com achados, severidade e recomendações. Use quando
  o usuário pedir avaliação de segurança, auditoria, skill de TCC, OpenCode ou
  relatório .md de segurança do projeto.
---

# Avaliação de Segurança — StudyHub

## Objetivo

Analisar o repositório StudyHub e produzir um relatório **`RELATORIO_AVALIACAO_SEGURANCA.md`** na **raiz do projeto**, com resultados objetivos da avaliação de segurança.

## Pré-requisitos

- Ler código backend (`backend/apps/`, `backend/config/`) e frontend (`frontend/src/`).
- Não expor segredos reais (`.env`, tokens, senhas) no relatório.
- Basear achados em evidências (arquivo, linha ou trecho).

## Checklist de análise

Copie e marque durante a execução:

```
- [ ] 1. Autenticação e sessão (JWT, login, hash de senha)
- [ ] 2. Autorização e isolamento de dados por aluno
- [ ] 3. Validação de entrada (senha, formulários, API)
- [ ] 4. Gestão de segredos (.env, .gitignore, variáveis)
- [ ] 5. Configuração do servidor (DEBUG, ALLOWED_HOSTS, CORS)
- [ ] 6. Proteção de dados (soft delete, logs, PII)
- [ ] 7. Uploads e arquivos (cadernos/imagens)
- [ ] 8. Integrações externas (Google OAuth, Gemini, Telegram)
- [ ] 9. Frontend (token no localStorage, XSS)
- [ ] 10. Testes automatizados de segurança existentes
```

## Áreas obrigatórias do StudyHub

| Área | Onde analisar |
|------|----------------|
| Login JWT | `apps/alunos/views.py`, `authentication.py`, `auth_service.py` |
| Senha forte | `apps/alunos/services/senha_validator.py`, `serializers.py` |
| Rotas protegidas | `permission_classes = [IsAuthenticated]` em views |
| Dono do recurso | `apps/cadernos/permissions.py`, querysets por `request.user` |
| Telegram | `apps/telegram/` — token só no backend, código temporário |
| Assistente IA | limite de uso, chave Gemini só no backend |
| Settings | `config/settings.py`, `backend/.env.example` |

## Classificação de severidade

| Nível | Critério |
|-------|----------|
| **Crítica** | Exploração remota, vazamento de credenciais, bypass de auth |
| **Alta** | Acesso indevido a dados de outro usuário, config insegura em produção |
| **Média** | Validação incompleta, hardening ausente, risco mitigável |
| **Baixa** | Melhoria de boas práticas, impacto limitado |
| **Informativa** | Ponto positivo ou observação |

## Formato do relatório (obrigatório)

Gravar na raiz: `RELATORIO_AVALIACAO_SEGURANCA.md`

```markdown
# Relatório de Avaliação de Segurança — StudyHub

**Data:** YYYY-MM-DD
**Escopo:** [backend, frontend, integrações]
**Metodologia:** Análise estática de código + checklist OWASP adaptado

## Resumo executivo
[2–4 frases: postura geral, principais riscos, principais pontos fortes]

## Pontuação resumida
| Categoria | Nota (0–10) | Status |
|-----------|-------------|--------|
| Autenticação | | |
| Autorização | | |
| Segredos e configuração | | |
| Validação de entrada | | |
| Integrações | | |

## Pontos fortes
- [lista com evidência]

## Achados
| ID | Severidade | Local | Descrição | Recomendação |
|----|------------|-------|-----------|--------------|
| S-01 | | | | |

## Recomendações prioritárias
1. ...
2. ...

## Conclusão
[adequado para TCC / requer hardening antes de produção]

## Anexo — arquivos analisados
- lista principal
```

## Regras de redação

1. Escrever em **português**.
2. Cada achado deve citar **arquivo** (ex.: `backend/config/settings.py`).
3. Diferenciar ambiente **desenvolvimento** vs **produção**.
4. Mencionar testes em `backend/apps/alunos/tests.py` e `backend/apps/telegram/tests.py` se existirem.
5. Não inventar vulnerabilidades sem evidência no código.

## Fluxo de execução

1. Explorar estrutura do repositório.
2. Percorrer checklist (seções 1–10).
3. Registrar achados com severidade.
4. Calcular notas por categoria (subjetivo, mas justificado).
5. Escrever `RELATORIO_AVALIACAO_SEGURANCA.md` na raiz.
6. Informar ao usuário o caminho do relatório e quantos achados por severidade.

## OpenCode / entrega AVA

Para a atividade acadêmica, o usuário deve enviar:

1. Este arquivo **`SKILL.md`** (skill do agente).
2. O **`RELATORIO_AVALIACAO_SEGURANCA.md`** gerado após executar a skill.

Comando sugerido no agente: *"Execute a skill avaliacao-seguranca-studyhub e gere o relatório .md"*.
