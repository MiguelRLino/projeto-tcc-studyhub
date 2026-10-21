const LABEL_PARENTESCO = {
  PAI: "Pai",
  MAE: "Mãe",
  OUTRO: "Outro responsável",
};

const LABEL_STATUS = {
  ATIVO: "Ativo",
  PENDENTE: "Convite pendente",
  FALHA_ENVIO: "Falha no envio",
};

export default function ResponsavelCard({
  item,
  onRemover,
  onReenviar,
  onCancelar,
  ocupado,
}) {
  const parentesco = LABEL_PARENTESCO[item.parentesco] || item.parentesco;
  const status = LABEL_STATUS[item.status] || item.status;
  const ativo = item.tipo === "vinculo";

  return (
    <article className="resp-card">
      <div className="resp-card-info">
        <strong>{item.nome}</strong>
        <span>Parentesco: {parentesco}</span>
        <span>E-mail: {item.email}</span>
        <span className={`resp-status resp-status--${item.status?.toLowerCase()}`}>
          Status: {status}
        </span>
      </div>
      <div className="resp-card-actions">
        {ativo ? (
          <button
            type="button"
            className="shell-btn-danger-ghost"
            disabled={ocupado}
            onClick={() => onRemover?.(item)}
          >
            Remover acesso
          </button>
        ) : (
          <>
            <button
              type="button"
              className="shell-btn-ghost"
              disabled={ocupado}
              onClick={() => onReenviar?.(item)}
            >
              Reenviar convite
            </button>
            <button
              type="button"
              className="shell-btn-danger-ghost"
              disabled={ocupado}
              onClick={() => onCancelar?.(item)}
            >
              Cancelar convite
            </button>
          </>
        )}
      </div>
    </article>
  );
}
