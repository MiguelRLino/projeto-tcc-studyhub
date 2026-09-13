# Relatório — Autenticação e Testes de Senha (StudyHub)

**Data:** 09/09/2026  
**Módulo:** `backend/apps/alunos/`  
**Comando executado:** `python manage.py test apps.alunos --verbosity=2`

---

## 1. Análise da autenticação

A autenticação do StudyHub **não usa o `User` padrão do Django**. O fluxo é customizado em torno do model `Aluno` e JWT.

### Componentes principais

| Arquivo | Função / classe | Responsabilidade |
|---------|-----------------|------------------|
| `views.py` | `AlunoLoginView.post()` | Valida e-mail/senha, verifica hash e emite JWT |
| `views.py` | `AlunoCadastroView.post()` | Cadastra aluno com senha hasheada |
| `services/auth_service.py` | `criar_token_acesso()` | Gera JWT com `id_aluno` e expiração |
| `services/auth_service.py` | `decodificar_token()` | Valida e decodifica JWT |
| `authentication.py` | `JWTAuthentication.authenticate()` | Lê `Authorization: Bearer`, anexa `Aluno` em `request.user` |
| `serializers.py` | `AlunoLoginSerializer` | Valida payload de login |
| `serializers.py` | `AlunoCadastroSerializer` | Valida cadastro e aplica hash (`make_password`) |
| `views.py` | `AlunoAlterarSenhaView.post()` | Troca senha autenticado (`check_password` + `make_password`) |

### Fluxo de login

```
POST /api/alunos/login/ { email, senha }
    → AlunoLoginSerializer.validate()
    → Aluno.objects.get(email__iexact=...)
    → check_password(senha, aluno.senha)
    → criar_token_acesso(id_aluno)
    → Response { access, aluno }
```

### Fluxo de rotas protegidas

```
Header: Authorization: Bearer <token>
    → JWTAuthentication.authenticate()
    → decodificar_token()
    → Aluno.objects.get(pk=id_aluno)
    → request.user = aluno
```

**Conclusão:** a função central de autenticação de credenciais é `AlunoLoginView.post()` (login) e `JWTAuthentication.authenticate()` (sessão via token). O serviço `criar_token_acesso()` / `decodificar_token()` implementa o JWT.

---

## 2. Regras de senha testadas

| Regra | Descrição |
|-------|-----------|
| R1 | Mínimo de **8 caracteres** |
| R2 | Pelo menos **1 letra maiúscula** |
| R3 | Pelo menos **1 número** |
| R4 | Pelo menos **1 caractere especial** (`!@#$%^&*(),.?":{}|<>_\-+=[]\\;'/`~`) |

Implementação: `backend/apps/alunos/services/senha_validator.py` → `validar_senha_forte()`

Aplicada em:
- Cadastro (`AlunoCadastroSerializer.validate_senha`)
- Alteração de senha (`AlunoAlterarSenhaSerializer`)
- Recuperação de senha (`AlunoRecuperarSenhaConfirmarSerializer.validate_senha_nova`)

> **Nota:** antes desta análise, o projeto validava apenas `min_length=8`. A validação completa (R1–R4) foi adicionada para alinhar backend e testes.

---

## 3. Resultado da execução

```
Ran 17 tests in ~12s
OK (17 passed, 0 failed, 0 errors)
```

| # | Teste | Resultado |
|---|-------|-----------|
| 1 | `SenhaValidatorTestCase.test_senha_valida_sem_erros` | ✅ PASS |
| 2 | `SenhaValidatorTestCase.test_senha_curta` | ✅ PASS |
| 3 | `SenhaValidatorTestCase.test_senha_sem_maiuscula` | ✅ PASS |
| 4 | `SenhaValidatorTestCase.test_senha_sem_numero` | ✅ PASS |
| 5 | `SenhaValidatorTestCase.test_senha_sem_especial` | ✅ PASS |
| 6 | `AuthServiceTestCase.test_criar_e_decodificar_token` | ✅ PASS |
| 7 | `AlunoAuthAPITestCase.test_login_sucesso` | ✅ PASS |
| 8 | `AlunoAuthAPITestCase.test_login_senha_incorreta` | ✅ PASS |
| 9 | `AlunoAuthAPITestCase.test_login_email_inexistente` | ✅ PASS |
| 10 | `AlunoAuthAPITestCase.test_jwt_autentica_rota_protegida` | ✅ PASS |
| 11 | `AlunoAuthAPITestCase.test_cadastro_senha_valida` | ✅ PASS |
| 12 | `AlunoAuthAPITestCase.test_cadastro_rejeita_senha_curta` | ✅ PASS |
| 13 | `AlunoAuthAPITestCase.test_cadastro_rejeita_sem_maiuscula` | ✅ PASS |
| 14 | `AlunoAuthAPITestCase.test_cadastro_rejeita_sem_numero` | ✅ PASS |
| 15 | `AlunoAuthAPITestCase.test_cadastro_rejeita_sem_especial` | ✅ PASS |
| 16 | `AlunoAuthAPITestCase.test_alterar_senha_rejeita_nova_senha_fraca` | ✅ PASS |
| 17 | `AlunoAuthAPITestCase.test_alterar_senha_sucesso` | ✅ PASS |

**Total:** 17 testes · **17 aprovados** · **0 falhas**

---

## 4. Arquivos criados / alterados

| Arquivo | Ação |
|---------|------|
| `backend/apps/alunos/services/senha_validator.py` | Criado — validação R1–R4 |
| `backend/apps/alunos/serializers.py` | Alterado — integração do validador |
| `backend/apps/alunos/tests.py` | Criado — 17 testes automatizados |
| `RELATORIO_TESTES_AUTENTICACAO.md` | Criado — este relatório |

---

## 5. Como reproduzir

```bash
cd backend
python manage.py test apps.alunos --verbosity=2
```

Senha válida usada nos testes de sucesso: `Senha@123`

---

## 6. Recomendações

1. Replicar as mesmas regras R1–R4 no **frontend** (cadastro, alterar senha, redefinir senha) para feedback imediato ao usuário.
2. Manter testes no CI/CD (`python manage.py test apps.alunos`) a cada alteração em autenticação.
3. Login continua aceitando senhas antigas já cadastradas; a validação forte aplica-se a **novas senhas** (cadastro, troca e recuperação).
