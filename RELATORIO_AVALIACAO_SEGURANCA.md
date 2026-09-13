# Relatório de Avaliação de Segurança — StudyHub

**Data:** 11/09/2026  
**Escopo:** Backend Django REST, frontend React (Vite), MySQL, integrações Google OAuth, Gemini IA e Telegram  
**Metodologia:** Análise estática de código, checklist OWASP adaptado e revisão dos testes automatizados existentes  
**Skill utilizada:** `.cursor/skills/avaliacao-seguranca-studyhub/SKILL.md`

---

## Resumo executivo

O StudyHub apresenta uma **base de segurança sólida para um projeto acadêmico**, com autenticação JWT customizada, senhas armazenadas com hash PBKDF2, isolamento de dados por aluno nas APIs principais e segredos externalizados em `.env`. Os principais riscos concentram-se em **configurações de desenvolvimento** (`DEBUG=True`, CORS local) que não devem ir para produção sem hardening, **token JWT no `localStorage`** (vulnerável a XSS) e **validação de upload baseada apenas em extensão** de arquivo. Não foram encontradas falhas críticas de bypass de autenticação nas rotas protegidas analisadas.

---

## Pontuação resumida

| Categoria | Nota (0–10) | Status |
|-----------|-------------|--------|
| Autenticação | 8,0 | Bom |
| Autorização | 8,5 | Bom |
| Segredos e configuração | 7,0 | Adequado (dev) |
| Validação de entrada | 7,5 | Bom |
| Integrações externas | 8,0 | Bom |
| Frontend / cliente | 6,5 | Melhorias recomendadas |
| **Média geral** | **7,6** | **Adequado para TCC; hardening necessário para produção** |

---

## Pontos fortes

| ID | Evidência | Descrição |
|----|-----------|-----------|
| F-01 | `serializers.py` + `make_password` | Senhas nunca persistidas em texto plano; hash via Django PBKDF2 |
| F-02 | `senha_validator.py` | Política de senha forte: 8+ chars, maiúscula, número e caractere especial |
| F-03 | `authentication.py` | JWT validado em cada requisição; `request.user` = `Aluno` autenticado |
| F-04 | `permissions.py` (cadernos) | Permissões por dono (`IsDonoCaderno`, `IsDonoPagina`) |
| F-05 | `views.py` (sistema_estudos, telegram) | Endpoints sensíveis exigem `IsAuthenticated` |
| F-06 | `.gitignore` | `.env` do backend e frontend ignorados pelo Git |
| F-07 | `telegram/conexao_service.py` | Vinculação Telegram via código temporário (10 min, uso único) — sem chat_id manual |
| F-08 | `telegram/services.py` | Token do bot Telegram nunca exposto em API ou respostas |
| F-09 | `assistente_ia/services.py` | Limite de 10 perguntas/hora por aluno; chave Gemini só no backend |
| F-10 | `apps/alunos/tests.py` | 17 testes automatizados de autenticação e validação de senha |

---

## Achados

| ID | Severidade | Local | Descrição | Recomendação |
|----|------------|-------|-----------|--------------|
| S-01 | **Alta** | `frontend/src/services/authService.js` | JWT armazenado em `localStorage`, acessível a scripts em caso de XSS | Migrar para cookies `HttpOnly` + `Secure` ou reduzir superfície XSS; considerar refresh token com vida curta |
| S-02 | **Alta** | `config/settings.py` | `DEBUG=True` e `ALLOWED_HOSTS` local por padrão | Em produção: `DEBUG=False`, hosts explícitos, HTTPS obrigatório |
| S-03 | **Média** | `config/settings.py` | `DEFAULT_PERMISSION_CLASSES = AllowAny` — cada view deve definir permissão explicitamente | Auditar todas as views; preferir `IsAuthenticated` como padrão global |
| S-04 | **Média** | `cadernos/views.py` (`ImagemUploadAPIView`) | Validação de upload por extensão (.jpg, .png…) sem verificação MIME/conteúdo real | Validar magic bytes; reprocessar imagem; rejeitar polyglot files |
| S-05 | **Média** | `config/settings.py` | JWT HS256 com expiração configurável (24h padrão) — sem revogação de token | Reduzir TTL; implementar blacklist ou refresh tokens para logout forçado |
| S-06 | **Média** | Frontend (Tiptap/cadernos) | Conteúdo HTML rico editado pelo usuário pode conter XSS se renderizado sem sanitização | Garantir sanitização na renderização/exportação PDF; CSP no frontend |
| S-07 | **Baixa** | `config/settings.py` | `CORS_ALLOW_CREDENTIALS=True` com origens fixas em dev | Restringir origens em produção ao domínio real do frontend |
| S-08 | **Baixa** | `config/urls.py` | Servir `/media/` em DEBUG — uploads acessíveis por URL | Em produção usar storage privado ou URLs assinadas |
| S-09 | **Baixa** | `JWTAuthentication` | Token inválido/expirado retorna anônimo (silencioso) em vez de 401 | Comportamento aceitável para rotas públicas; documentar para o frontend |
| S-10 | **Informativa** | `telegram/models.py` | Constraint unique evita notificações duplicadas | Boa prática anti-abuso/spam |
| S-11 | **Informativa** | `recuperacao_senha_service.py` | Token de reset com propósito (`password_reset`) e expiração | Implementação correta de fluxo de recuperação |

---

## Detalhamento por categoria

### 1. Autenticação e sessão

- **Login:** `AlunoLoginView` usa `check_password` e emite JWT via `criar_token_acesso()`.
- **Cadastro:** senha validada por `validar_senha_forte()` antes do hash.
- **Google OAuth:** credencial verificada server-side com `google.oauth2.id_token`.
- **Recuperação de senha:** token JWT de propósito único com expiração.

**Risco residual:** tokens longos (24h) no cliente sem revogação.

### 2. Autorização

- Disciplinas, tarefas, cadernos e Telegram filtram por `request.user` (aluno autenticado).
- Cadernos implementam permissões de objeto explícitas.
- Testes Telegram confirmam que aluno A não altera configuração de aluno B.

### 3. Gestão de segredos

- `DJANGO_SECRET_KEY`, `JWT_SECRET_KEY`, `GEMINI_API_KEY`, `TELEGRAM_BOT_TOKEN` via `.env`.
- `.env.example` documenta variáveis sem valores reais.
- **Atenção:** garantir que `.env` nunca seja commitado (já está no `.gitignore`).

### 4. Integrações

| Integração | Controle |
|------------|----------|
| Telegram | Token só backend; conexão por código temporário |
| Gemini | Chave só backend; rate limit por aluno |
| Google | Client ID público; validação do JWT Google no servidor |

### 5. Testes de segurança existentes

| Módulo | Testes | Foco |
|--------|--------|------|
| `apps.alunos` | 17 | Login, JWT, senha forte, cadastro |
| `apps.telegram` | 22 | Auth, código expiração, anti-duplicata, token oculto |
| `apps.cadernos` | Sim | Permissões e CRUD isolado |

---

## Recomendações prioritárias

1. **Produção:** definir `DEBUG=False`, HTTPS, `ALLOWED_HOSTS` e CORS restritos.
2. **Token:** avaliar cookies `HttpOnly` ou refresh token de curta duração.
3. **Uploads:** validar tipo real do arquivo (conteúdo), não só extensão.
4. **Permissões DRF:** alterar default para `IsAuthenticated` e usar `AllowAny` só em rotas públicas.
5. **Frontend:** replicar validação de senha forte no cadastro/redefinição (UX + defesa em profundidade).
6. **Headers de segurança:** adicionar `SECURE_*`, HSTS e CSP quando publicar.

---

## Conclusão

O StudyHub demonstra **consciência de segurança adequada para um TCC**, com autenticação bem estruturada, hash de senhas, isolamento multi-usuário e integrações externas tratadas no backend. Para ambiente **acadêmico e demonstração**, o nível é **satisfatório**. Para **produção pública**, aplicar as recomendações S-01 a S-06 antes do deploy.

---

## Anexo — arquivos principais analisados

- `backend/config/settings.py`
- `backend/apps/alunos/authentication.py`
- `backend/apps/alunos/views.py`
- `backend/apps/alunos/serializers.py`
- `backend/apps/alunos/services/auth_service.py`
- `backend/apps/alunos/services/senha_validator.py`
- `backend/apps/cadernos/permissions.py`
- `backend/apps/cadernos/views.py`
- `backend/apps/telegram/conexao_service.py`
- `backend/apps/telegram/services.py`
- `backend/apps/assistente_ia/services.py`
- `frontend/src/services/api.js`
- `frontend/src/services/authService.js`
- `.gitignore`
- `backend/.env.example`

---

## Entrega AVA (atividade Skill)

Arquivos para upload individual:

1. **Skill:** `.cursor/skills/avaliacao-seguranca-studyhub/SKILL.md`
2. **Relatório:** `RELATORIO_AVALIACAO_SEGURANCA.md` (este arquivo)
