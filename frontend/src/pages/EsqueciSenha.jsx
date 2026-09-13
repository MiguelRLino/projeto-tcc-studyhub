import { useState } from "react";
import { Link } from "react-router-dom";
import { Mail } from "lucide-react";
import AuthShell from "../components/AuthShell";
import AuthInput from "../components/AuthInput";
import { extrairMensagemErro } from "../services/api";
import { solicitarRecuperacaoSenha } from "../services/recuperacaoService";

export default function EsqueciSenha() {
  const [email, setEmail] = useState("");
  const [erro, setErro] = useState("");
  const [sucesso, setSucesso] = useState("");
  const [carregando, setCarregando] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setErro("");
    setSucesso("");
    setCarregando(true);
    try {
      const { data } = await solicitarRecuperacaoSenha(email.trim());
      setSucesso(
        data.mensagem ||
          "Se este e-mail estiver cadastrado, você receberá um link para redefinir a senha em instantes.",
      );
    } catch (err) {
      setErro(extrairMensagemErro(err));
    } finally {
      setCarregando(false);
    }
  }

  return (
    <AuthShell
      title="Esqueceu a senha?"
      subtitle="Informe seu e-mail e enviaremos um link para criar uma nova senha"
    >
      {sucesso ? (
        <div className="auth-recuperacao-ok">
          <p className="auth-recuperacao-msg">{sucesso}</p>
          <Link to="/login" className="auth-link auth-recuperacao-voltar">
            Voltar ao login
          </Link>
        </div>
      ) : (
        <form onSubmit={handleSubmit} noValidate>
          <AuthInput
            id="email-recuperar"
            label="Email"
            type="email"
            icon={Mail}
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="seu@email.com"
            required
          />

          {erro ? (
            <p className="auth-error" role="alert">
              {erro}
            </p>
          ) : null}

          <button type="submit" className="auth-submit" disabled={carregando}>
            {carregando ? "Enviando…" : "Enviar link"}
          </button>

          <div className="auth-card-footer">
            <Link to="/login" className="auth-link">
              Voltar ao login
            </Link>
          </div>
        </form>
      )}
    </AuthShell>
  );
}
