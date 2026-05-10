import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Lock, Mail, User } from "lucide-react";
import AuthShell from "../components/AuthShell";
import AuthInput from "../components/AuthInput";
import { api, extrairMensagemErro } from "../services/api";
import { salvarSessao } from "../services/authService";

export default function Cadastro() {
  const navigate = useNavigate();
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setErro("");
    setCarregando(true);
    try {
      const { data } = await api.post("/api/alunos/cadastro/", {
        nome,
        email,
        senha,
      });
      salvarSessao(data.access, data.aluno);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setErro(extrairMensagemErro(err));
    } finally {
      setCarregando(false);
    }
  }

  return (
    <AuthShell
      title="Crie sua conta no StudyHub"
      subtitle="Preencha os dados abaixo para começar a organizar seus estudos"
    >
      <form onSubmit={handleSubmit} noValidate>
        <AuthInput
          id="nome"
          label="Nome completo"
          type="text"
          icon={User}
          autoComplete="name"
          value={nome}
          onChange={(e) => setNome(e.target.value)}
          placeholder="Seu nome"
          required
          maxLength={100}
        />
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
          maxLength={150}
        />
        <AuthInput
          id="senha"
          label="Senha"
          type="password"
          icon={Lock}
          autoComplete="new-password"
          value={senha}
          onChange={(e) => setSenha(e.target.value)}
          placeholder="Mínimo 8 caracteres"
          required
          minLength={8}
        />

        {erro ? (
          <p className="auth-error" role="alert">
            {erro}
          </p>
        ) : null}

        <button type="submit" className="auth-submit" disabled={carregando}>
          {carregando ? "Criando conta…" : "Criar conta"}
        </button>

        <div className="auth-card-footer">
          Já tem uma conta?{" "}
          <Link to="/login" className="auth-link">
            Entrar
          </Link>
        </div>
      </form>
    </AuthShell>
  );
}
