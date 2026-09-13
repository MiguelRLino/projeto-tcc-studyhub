import { useMemo, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { CheckCircle2, KeyRound, Lock } from "lucide-react";
import AuthShell from "../components/AuthShell";
import AuthInput from "../components/AuthInput";
import { extrairMensagemErro } from "../services/api";
import { confirmarNovaSenha } from "../services/recuperacaoService";

function RegraSenha({ ok, children }) {
  return (
    <li className={ok ? "ok" : ""}>
      <span className="auth-regra-dot" aria-hidden />
      {children}
    </li>
  );
}

export default function RedefinirSenha() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const token = useMemo(() => {
    const bruto = params.get("token");
    if (!bruto) return "";
    try {
      return decodeURIComponent(bruto.trim());
    } catch {
      return bruto.trim();
    }
  }, [params]);

  const [senha, setSenha] = useState("");
  const [confirmacao, setConfirmacao] = useState("");
  const [erro, setErro] = useState("");
  const [sucesso, setSucesso] = useState("");
  const [carregando, setCarregando] = useState(false);

  const temMinimo = senha.length >= 8;
  const senhasIguais = senha.length > 0 && senha === confirmacao;

  async function handleSubmit(e) {
    e.preventDefault();
    setErro("");
    if (!token) {
      setErro("Link inválido. Solicite uma nova recuperação de senha.");
      return;
    }
    if (!temMinimo) {
      setErro("A senha deve ter pelo menos 8 caracteres.");
      return;
    }
    if (!senhasIguais) {
      setErro("As senhas não coincidem.");
      return;
    }
    setCarregando(true);
    try {
      const { data } = await confirmarNovaSenha(token, senha);
      setSucesso(data.mensagem || "Senha redefinida com sucesso.");
    } catch (err) {
      setErro(extrairMensagemErro(err));
    } finally {
      setCarregando(false);
    }
  }

  if (!token && !sucesso) {
    return (
      <AuthShell
        title="Link inválido"
        subtitle="O endereço está incompleto ou o link já expirou"
      >
        <div className="auth-recuperacao-ok">
          <p className="auth-recuperacao-msg">
            Abra o link completo que enviamos por e-mail ou solicite um novo. Os links
            expiram em 1 hora.
          </p>
          <Link to="/esqueci-senha" className="auth-submit auth-submit--link">
            Solicitar novo link
          </Link>
          <div className="auth-card-footer">
            <Link to="/login" className="auth-link">
              Voltar ao login
            </Link>
          </div>
        </div>
      </AuthShell>
    );
  }

  if (sucesso) {
    return (
      <AuthShell
        title="Senha atualizada!"
        subtitle="Sua nova senha já está ativa no StudyHub"
      >
        <div className="auth-recuperacao-ok auth-redefinir-sucesso">
          <div className="auth-redefinir-icon-ok" aria-hidden>
            <CheckCircle2 size={40} strokeWidth={2} />
          </div>
          <p className="auth-recuperacao-msg">{sucesso}</p>
          <p className="auth-recuperacao-hint">Use a nova senha para entrar na sua conta.</p>
          <button
            type="button"
            className="auth-submit"
            onClick={() => navigate("/login", { replace: true })}
          >
            Ir para o login
          </button>
        </div>
      </AuthShell>
    );
  }

  return (
    <AuthShell
      title="Redefinir senha"
      subtitle="Escolha uma nova senha segura para sua conta"
    >
      <div className="auth-redefinir-badge" aria-hidden>
        <KeyRound size={22} />
      </div>

      <form onSubmit={handleSubmit} noValidate>
        <AuthInput
          id="senha-nova"
          label="Nova senha"
          type="password"
          icon={Lock}
          autoComplete="new-password"
          value={senha}
          onChange={(e) => setSenha(e.target.value)}
          placeholder="Mínimo 8 caracteres"
          required
          minLength={8}
          permitirAlternarVisibilidade
        />
        <AuthInput
          id="senha-confirma"
          label="Confirmar nova senha"
          type="password"
          icon={Lock}
          autoComplete="new-password"
          value={confirmacao}
          onChange={(e) => setConfirmacao(e.target.value)}
          placeholder="Repita a nova senha"
          required
          minLength={8}
          permitirAlternarVisibilidade
        />

        <ul className="auth-regras-senha" aria-label="Requisitos da senha">
          <RegraSenha ok={temMinimo}>Pelo menos 8 caracteres</RegraSenha>
          <RegraSenha ok={senhasIguais}>Senhas iguais nos dois campos</RegraSenha>
        </ul>

        {erro ? (
          <p className="auth-error" role="alert">
            {erro}
          </p>
        ) : null}

        <button
          type="submit"
          className="auth-submit"
          disabled={carregando || !temMinimo || !senhasIguais}
        >
          {carregando ? "Salvando…" : "Salvar nova senha"}
        </button>

        <div className="auth-card-footer">
          <Link to="/login" className="auth-link">
            Voltar ao login
          </Link>
        </div>
      </form>
    </AuthShell>
  );
}
