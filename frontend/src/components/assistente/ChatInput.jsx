import { Loader2, Send } from "lucide-react";

const MAX_CHARS = 2000;

export default function ChatInput({
  valor,
  onChange,
  onEnviar,
  carregando,
  placeholder = "Digite sua dúvida...",
}) {
  const restantes = MAX_CHARS - (valor?.length || 0);

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!carregando && valor?.trim()) onEnviar();
    }
  }

  return (
    <div className="ia-input-wrap">
      <textarea
        className="ia-input"
        value={valor}
        onChange={(e) => onChange(e.target.value.slice(0, MAX_CHARS))}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        rows={3}
        disabled={carregando}
        maxLength={MAX_CHARS}
      />
      <div className="ia-input-footer">
        <span className="ia-input-count">{restantes} caracteres restantes</span>
        <button
          type="button"
          className="ia-btn-enviar"
          onClick={onEnviar}
          disabled={carregando || !valor?.trim()}
        >
          {carregando ? (
            <>
              <Loader2 size={16} className="spin" />
              Pensando...
            </>
          ) : (
            <>
              <Send size={16} />
              Enviar
            </>
          )}
        </button>
      </div>
    </div>
  );
}

export { MAX_CHARS as IA_MAX_CHARS };
