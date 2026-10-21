import { obterUsuario } from "../services/authService";

export default function ResponsavelPerfilPage() {
  const usuario = obterUsuario();
  return (
    <div className="shell-page">
      <header className="shell-page-head">
        <h1>Perfil</h1>
        <p>Dados da sua conta de responsável.</p>
      </header>
      <section className="shell-perfil-card">
        <p>
          <strong>Nome:</strong> {usuario?.nome || "—"}
        </p>
        <p>
          <strong>E-mail:</strong> {usuario?.email || "—"}
        </p>
        <p>
          <strong>Tipo de conta:</strong> Responsável
        </p>
      </section>
    </div>
  );
}
