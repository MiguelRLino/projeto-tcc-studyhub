import { useEffect, useState } from "react";
import { X } from "lucide-react";
import { extrairMensagemErro } from "../../services/api";

const CORES = ["#6366f1", "#3b82f6", "#22c55e", "#fb923c", "#eab308", "#ec4899", "#a855f7"];

export default function ModalCaderno({
  aberto,
  modo,
  caderno,
  disciplinas,
  onFechar,
  onSalvar,
}) {
  const [titulo, setTitulo] = useState("");
  const [descricao, setDescricao] = useState("");
  const [cor, setCor] = useState(CORES[0]);
  const [idDisciplina, setIdDisciplina] = useState("");
  const [erro, setErro] = useState("");
  const [salvando, setSalvando] = useState(false);

  useEffect(() => {
    if (!aberto) return;
    setTitulo(caderno?.titulo || "");
    setDescricao(caderno?.descricao || "");
    setCor(caderno?.cor || CORES[0]);
    setIdDisciplina(caderno?.id_disciplina ? String(caderno.id_disciplina) : "");
    setErro("");
  }, [aberto, caderno]);

  if (!aberto) return null;

  async function handleSubmit(e) {
    e.preventDefault();
    if (!titulo.trim()) {
      setErro("Informe o título do caderno.");
      return;
    }
    setSalvando(true);
    setErro("");
    try {
      await onSalvar({
        titulo: titulo.trim(),
        descricao: descricao.trim(),
        cor,
        id_disciplina: idDisciplina ? Number(idDisciplina) : null,
      });
      onFechar();
    } catch (err) {
      setErro(extrairMensagemErro(err));
    } finally {
      setSalvando(false);
    }
  }

  return (
    <div className="caderno-modal-overlay" onClick={onFechar}>
      <div
        className="caderno-modal"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-labelledby="modal-caderno-titulo"
      >
        <header className="caderno-modal-header">
          <h2 id="modal-caderno-titulo">
            {modo === "editar" ? "Editar caderno" : "Novo caderno"}
          </h2>
          <button type="button" className="caderno-icon-btn" onClick={onFechar}>
            <X size={18} />
          </button>
        </header>
        <form onSubmit={handleSubmit} className="caderno-modal-body">
          {erro && <p className="caderno-erro">{erro}</p>}
          <label>
            Título
            <input
              value={titulo}
              onChange={(e) => setTitulo(e.target.value)}
              maxLength={150}
              autoFocus
            />
          </label>
          <label>
            Descrição (opcional)
            <textarea
              value={descricao}
              onChange={(e) => setDescricao(e.target.value)}
              rows={3}
              maxLength={500}
            />
          </label>
          <label>
            Disciplina (opcional)
            <select
              value={idDisciplina}
              onChange={(e) => setIdDisciplina(e.target.value)}
            >
              <option value="">Nenhuma</option>
              {disciplinas.map((d) => (
                <option key={d.id_disciplina} value={d.id_disciplina}>
                  {d.nome}
                </option>
              ))}
            </select>
          </label>
          <div className="caderno-modal-cores">
            <span>Cor</span>
            <div className="caderno-modal-swatches">
              {CORES.map((c) => (
                <button
                  key={c}
                  type="button"
                  className={`caderno-swatch${cor === c ? " is-active" : ""}`}
                  style={{ background: c }}
                  onClick={() => setCor(c)}
                />
              ))}
            </div>
          </div>
          <footer className="caderno-modal-footer">
            <button type="button" className="caderno-btn ghost" onClick={onFechar}>
              Cancelar
            </button>
            <button type="submit" className="caderno-btn primary" disabled={salvando}>
              {salvando ? "Salvando…" : "Salvar"}
            </button>
          </footer>
        </form>
      </div>
    </div>
  );
}
