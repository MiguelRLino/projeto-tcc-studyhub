import { useEffect, useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { GoogleLogin } from "@react-oauth/google";
import { Lock, Mail } from "lucide-react";
import AuthShell from "../components/AuthShell";
import AuthInput from "../components/AuthInput";
import { api, extrairMensagemErro } from "../services/api";
import { salvarSessao } from "../services/authService";

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || "";

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from || "/dashboard";

  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [lembrar, setLembrar] = useState(false);
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(false);

  useEffect(() => {
    const salvo = localStorage.getItem("studyhub_lembrar_email");
    if (salvo) {
      setEmail(salvo);
      setLembrar(true);
    }
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setErro("");
    setCarregando(true);
    try {
      const { data } = await api.post("/api/alunos/login/", { email, senha });
      salvarSessao(data.access, data.aluno);
      if (lembrar) {
        localStorage.setItem("studyhub_lembrar_email", email.trim());
      } else {
        localStorage.removeItem("studyhub_lembrar_email");
      }
      navigate(from === "/login" ? "/dashboard" : from, { replace: true });
    } catch (err) {
      setErro(extrairMensagemErro(err));
    } finally {
      setCarregando(false);
    }
  }

  async function enviarCredentialGoogle(credential) {
    if (!credential) return;
    setErro("");
    setCarregando(true);
    try {
      const { data } = await api.post("/api/alunos/login/google/", { credential });
      salvarSessao(data.access, data.aluno);
      navigate(from === "/login" ? "/dashboard" : from, { replace: true });
    } catch (err) {
      setErro(extrairMensagemErro(err));
    } finally {
      setCarregando(false);
    }
  }

  return (
    <AuthShell
      title="Bem-vindo ao StudyHub"
      subtitle="Organize seus estudos de forma inteligente"
    >
      <form onSubmit={handleSubmit} noValidate>
        <AuthInput
          id="email"
          label="Email"
          type="email"
          icon={Mail}
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="seu@email.com"
          required
        />
        <AuthInput
          id="senha"
          label="Senha"
          type="password"
          icon={Lock}
          autoComplete="current-password"
          value={senha}
          onChange={(e) => setSenha(e.target.value)}
          placeholder="••••••••"
          required
        />

        <div className="auth-row-between">
          <label className="auth-check">
            <input
              type="checkbox"
              checked={lembrar}
              onChange={(e) => setLembrar(e.target.checked)}
            />
            Lembrar de mim
          </label>
          <a
            href="#"
            className="auth-link"
            onClick={(e) => {
              e.preventDefault();
            }}
          >
            Esqueceu a senha?
          </a>
        </div>

        <button type="submit" className="auth-submit" disabled={carregando}>
          {carregando ? "Entrando…" : "Entrar"}
        </button>
      </form>

      {erro ? (
        <p className="auth-error" role="alert">
          {erro}
        </p>
      ) : null}

      {googleClientId ? (
        <>
          <div className="auth-divider" role="separator">
            <span>ou</span>
          </div>
          <p className="auth-google-hint">Entre com sua conta Google (opcional)</p>
          <div className={`auth-google-wrap${carregando ? " auth-google-wrap--busy" : ""}`}>
            <GoogleLogin
              onSuccess={(res) => enviarCredentialGoogle(res.credential)}
              onError={() => setErro("Não foi possível usar o Google. Tente de novo.")}
              theme="filled_black"
              size="large"
              text="continue_with"
              shape="pill"
              width={340}
              locale="pt-BR"
            />
          </div>
        </>
      ) : (
        <p className="auth-google-missing">
          Para habilitar o botão Google, defina <code>VITE_GOOGLE_CLIENT_ID</code> no{" "}
          <code>.env</code> do frontend.
        </p>
      )}

      <div className="auth-card-footer">
        Não tem uma conta?{" "}
        <Link to="/cadastro" className="auth-link">
          Criar conta
        </Link>
      </div>
    </AuthShell>
  );
}
