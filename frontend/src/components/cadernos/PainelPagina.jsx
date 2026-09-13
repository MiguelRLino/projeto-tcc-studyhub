import {
  Copy,
  FileDown,
  Printer,
  Star,
  Trash2,
  FolderInput,
  Sparkles,
} from "lucide-react";

function formatarData(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("pt-BR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function PainelPagina({
  pagina,
  metricas,
  onFavoritar,
  onDuplicar,
  onMover,
  onExportarPdf,
  onImprimir,
  onExcluir,
  onIaPlaceholder,
  acaoCarregando,
}) {
  if (!pagina) return null;

  const m = metricas || {
    palavras: pagina.quantidade_palavras || 0,
    caracteres: pagina.quantidade_caracteres || 0,
    leituraMin: pagina.tempo_leitura_min || 0,
  };

  return (
    <aside className="caderno-painel">
      <h3>Informações</h3>
      <dl className="caderno-painel-meta">
        <div>
          <dt>Criada em</dt>
          <dd>{formatarData(pagina.data_criacao)}</dd>
        </div>
        <div>
          <dt>Última edição</dt>
          <dd>{formatarData(pagina.data_atualizacao)}</dd>
        </div>
        <div>
          <dt>Caderno</dt>
          <dd>{pagina.caderno_titulo || "—"}</dd>
        </div>
        <div>
          <dt>Palavras</dt>
          <dd>{m.palavras}</dd>
        </div>
        <div>
          <dt>Caracteres</dt>
          <dd>{m.caracteres}</dd>
        </div>
        <div>
          <dt>Leitura</dt>
          <dd>{m.leituraMin <= 0 ? "< 1 min" : `~${m.leituraMin} min`}</dd>
        </div>
      </dl>

      <h3>Ações</h3>
      <div className="caderno-painel-acoes">
        <button
          type="button"
          className={`caderno-painel-btn${pagina.favorita ? " is-active" : ""}`}
          onClick={onFavoritar}
          disabled={acaoCarregando}
        >
          <Star size={16} />
          {pagina.favorita ? "Desfavoritar" : "Favoritar"}
        </button>
        <button
          type="button"
          className="caderno-painel-btn"
          onClick={onDuplicar}
          disabled={acaoCarregando}
        >
          <Copy size={16} />
          Duplicar
        </button>
        <button
          type="button"
          className="caderno-painel-btn"
          onClick={onMover}
          disabled={acaoCarregando}
        >
          <FolderInput size={16} />
          Mover
        </button>
        <button type="button" className="caderno-painel-btn" onClick={onExportarPdf}>
          <FileDown size={16} />
          Exportar PDF
        </button>
        <button type="button" className="caderno-painel-btn" onClick={onImprimir}>
          <Printer size={16} />
          Imprimir
        </button>
        <button
          type="button"
          className="caderno-painel-btn caderno-painel-btn--ia"
          onClick={onIaPlaceholder}
        >
          <Sparkles size={16} />
          Perguntar para IA
        </button>
        <button
          type="button"
          className="caderno-painel-btn danger"
          onClick={onExcluir}
          disabled={acaoCarregando}
        >
          <Trash2 size={16} />
          Excluir
        </button>
      </div>
    </aside>
  );
}
