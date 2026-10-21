import { useState } from "react";
import { extrairMensagemErro } from "../../services/api";
import { convidarResponsavel } from "../../services/responsavelService";

export default function CadastrarResponsavelModal({ aberto, onFechar, onSucesso }) {
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [parentesco, setParentesco] = useState("MAE");
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  if (!aberto) return null;

  async function handleSubmit(e) {
    e.preventDefault();
    setErro("");
    setEnviando(true);
    try {
      const { data } = await convidarResponsavel({ nome, email, parentesco });
      onSucesso?.(data);
      setNome("");
      setEmail("");
      setParentesco("MAE");
      onFechar?.();
    } catch (err) {
      setErro(extrairMensagemErro(err));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="shell-modal-overlay" role="presentation" onClick={onFechar}>
      <div
        className="shell-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-resp-titulo"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id="modal-resp-titulo">Cadastrar responsável</h2>
        <p className="shell-modal-desc">
          Enviaremos um convite por e-mail para a pessoa criar o acesso e acompanhar
          seus estudos.
        </p>
        <form onSubmit={handleSubmit}>
          <label className="shell-field">
            <span>Nome completo</span>
            <input
              type="text"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              required
              maxLength={100}
            />
          </label>
          <label className="shell-field">
            <span>E-mail</span>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </label>
          <label className="shell-field">
            <span>Parentesco</span>
            <select
              value={parentesco}
              onChange={(e) => setParentesco(e.target.value)}
            >
              <option value="MAE">Mãe</option>
              <option value="PAI">Pai</option>
              <option value="OUTRO">Outro responsável</option>
            </select>
          </label>
          {erro ? <p className="shell-form-erro">{erro}</p> : null}
          <div className="shell-modal-actions">
            <button type="button" className="shell-btn-ghost" onClick={onFechar}>
              Cancelar
            </button>
            <button type="submit" className="shell-btn-primary" disabled={enviando}>
              {enviando ? "Enviando…" : "Enviar convite"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
