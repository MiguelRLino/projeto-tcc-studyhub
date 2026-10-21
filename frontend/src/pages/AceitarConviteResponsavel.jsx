import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Lock, UserPlus } from "lucide-react";
import AuthShell from "../components/AuthShell";
import AuthInput from "../components/AuthInput";
import { extrairMensagemErro } from "../services/api";
import {
  destinoPosLogin,
  ehResponsavel,
  obterUsuario,
  salvarSessao,
  TIPO_RESPONSAVEL,
} from "../services/authService";
import { aceitarConvite, validarConvite } from "../services/responsavelService";

export default function AceitarConviteResponsavel() {
  const { token } = useParams();
  const navigate = useNavigate();
  const tokenLimpo = useMemo(() => (token || "").trim(), [token]);

  const [info, setInfo] = useState(null);
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(true);
  const [senha, setSenha] = useState("");
  const [confirmacao, setConfirmacao] = useState("");
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    let ativo = true;
    async function carregar() {
      if (!tokenLimpo) {
        setErro("Link de convite inválido.");
        setCarregando(false);
        return;
      }
      try {
        const { data } = await validarConvite(tokenLimpo);
        if (ativo) setInfo(data);
      } catch (e) {
        if (ativo) setErro(extrairMensagemErro(e));
      } finally {
        if (ativo) setCarregando(false);
      }
    }
    carregar();
    return () => {
      ativo = false;
    };
  }, [tokenLimpo]);

  async function handleCriarConta(e) {
    e.preventDefault();
    setErro("");
    if (senha.length < 8) {
      setErro("A senha deve ter pelo menos 8 caracteres.");
      return;
    }
    if (senha !== confirmacao) {
      setErro("As senhas não coincidem.");
      return;
    }
    setEnviando(true);
    try {
      const { data } = await aceitarConvite({
        token: tokenLimpo,
        senha,
        senha_confirmacao: confirmacao,
      });
      salvarSessao(data.access, data.usuario, data.tipo || TIPO_RESPONSAVEL);
      navigate(destinoPosLogin(TIPO_RESPONSAVEL), { replace: true });
    } catch (err) {
      setErro(extrairMensagemErro(err));
    } finally {
      setEnviando(false);
    }
  }

  async function handleAceitarLogado() {
    setErro("");
    setEnviando(true);
    try {
      const { data } = await aceitarConvite({ token: tokenLimpo });
      salvarSessao(data.access, data.usuario, data.tipo || TIPO_RESPONSAVEL);
      navigate(destinoPosLogin(TIPO_RESPONSAVEL), { replace: true });
    } catch (err) {
      setErro(extrairMensagemErro(err));
    } finally {
      setEnviando(false);
    }
  }

  if (carregando) {
    return (
      <AuthShell title="Validando convite" subtitle="Aguarde um instante">
        <p className="auth-recuperacao-msg">Verificando o link…</p>
      </AuthShell>
    );
  }

  if (!info) {
    return (
      <AuthShell title="Convite indisponível" subtitle="Não foi possível validar o link">
        <p className="auth-recuperacao-msg">{erro || "Convite inválido."}</p>
        <Link to="/login" className="auth-submit auth-submit--link">
          Ir para o login
        </Link>
      </AuthShell>
    );
  }

  const usuarioLogado = obterUsuario();
  const mesmoEmail =
    ehResponsavel() &&
    usuarioLogado?.email &&
    usuarioLogado.email.toLowerCase() === info.email_convidado.toLowerCase();

  if (info.conta_existe || mesmoEmail) {
    return (
      <AuthShell
        title="Aceitar convite"
        subtitle={`Acompanhar ${info.nome_aluno} no StudyHub`}
      >
        <p className="auth-recuperacao-msg">
          Convite para <strong>{info.nome_convidado}</strong> ({info.email_convidado}).
        </p>
        {erro ? <p className="auth-error">{erro}</p> : null}
        {mesmoEmail ? (
          <button
            type="button"
            className="auth-submit"
            disabled={enviando}
            onClick={handleAceitarLogado}
          >
            {enviando ? "Aceitando…" : "Aceitar convite"}
          </button>
        ) : (
          <>
            <p className="auth-recuperacao-msg">
              Já existe uma conta para este e-mail. Entre e depois abra novamente o
              link do convite.
            </p>
            <Link
              to="/login"
              state={{ from: `/convite/responsavel/${tokenLimpo}` }}
              className="auth-submit auth-submit--link"
            >
              Fazer login
            </Link>
          </>
        )}
      </AuthShell>
    );
  }

  return (
    <AuthShell
      title="Criar conta de responsável"
      subtitle={`Convite de ${info.nome_aluno}`}
    >
      <p className="auth-recuperacao-msg">
        Olá, <strong>{info.nome_convidado}</strong>! Defina uma senha para
        acompanhar os estudos no StudyHub.
      </p>
      <form onSubmit={handleCriarConta} noValidate>
        <AuthInput
          id="nome-convite"
          label="Nome"
          type="text"
          icon={UserPlus}
          value={info.nome_convidado}
          readOnly
        />
        <AuthInput
          id="email-convite"
          label="E-mail"
          type="email"
          value={info.email_convidado}
          readOnly
        />
        <AuthInput
          id="senha-convite"
          label="Senha"
          type="password"
          icon={Lock}
          value={senha}
          onChange={(e) => setSenha(e.target.value)}
          autoComplete="new-password"
          required
        />
        <AuthInput
          id="senha-confirm"
          label="Confirmar senha"
          type="password"
          icon={Lock}
          value={confirmacao}
          onChange={(e) => setConfirmacao(e.target.value)}
          autoComplete="new-password"
          required
        />
        {erro ? <p className="auth-error">{erro}</p> : null}
        <button type="submit" className="auth-submit" disabled={enviando}>
          {enviando ? "Criando…" : "Criar conta e aceitar convite"}
        </button>
      </form>
    </AuthShell>
  );
}
