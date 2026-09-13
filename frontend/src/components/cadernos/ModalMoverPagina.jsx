import { useEffect, useState } from "react";
import { X } from "lucide-react";
import { extrairMensagemErro } from "../../services/api";

export default function ModalMoverPagina({
  aberto,
  pagina,
  cadernos,
  onFechar,
  onMover,
}) {
  const [destinoId, setDestinoId] = useState("");
  const [erro, setErro] = useState("");
  const [salvando, setSalvando] = useState(false);

  useEffect(() => {
    if (!aberto) return;
    setDestinoId("");
    setErro("");
  }, [aberto]);

  if (!aberto || !pagina) return null;

  const opcoes = cadernos.filter((c) => c.id_caderno !== pagina.id_caderno);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!destinoId) {
      setErro("Selecione o caderno de destino.");
      return;
    }
    setSalvando(true);
    setErro("");
    try {
      await onMover(Number(destinoId));
      onFechar();
    } catch (err) {
      setErro(extrairMensagemErro(err));
    } finally {
      setSalvando(false);
    }
  }

  return (
    <div className="caderno-modal-overlay" onClick={onFechar}>
      <div className="caderno-modal" onClick={(e) => e.stopPropagation()}>
        <header className="caderno-modal-header">
          <h2>Mover página</h2>
          <button type="button" className="caderno-icon-btn" onClick={onFechar}>
            <X size={18} />
          </button>
        </header>
        <form onSubmit={handleSubmit} className="caderno-modal-body">
          <p className="caderno-muted">
            Mover &quot;{pagina.titulo}&quot; para outro caderno.
          </p>
          {erro && <p className="caderno-erro">{erro}</p>}
          <label>
            Caderno de destino
            <select
              value={destinoId}
              onChange={(e) => setDestinoId(e.target.value)}
            >
              <option value="">Selecione…</option>
              {opcoes.map((c) => (
                <option key={c.id_caderno} value={c.id_caderno}>
                  {c.titulo}
                </option>
              ))}
            </select>
          </label>
          {opcoes.length === 0 && (
            <p className="caderno-muted">Crie outro caderno para mover esta página.</p>
          )}
          <footer className="caderno-modal-footer">
            <button type="button" className="caderno-btn ghost" onClick={onFechar}>
              Cancelar
            </button>
            <button
              type="submit"
              className="caderno-btn primary"
              disabled={salvando || opcoes.length === 0}
            >
              {salvando ? "Movendo…" : "Mover"}
            </button>
          </footer>
        </form>
      </div>
    </div>
  );
}
