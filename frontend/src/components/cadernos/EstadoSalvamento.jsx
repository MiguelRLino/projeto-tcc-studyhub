import { AlertCircle, Check, Loader2 } from "lucide-react";

const ROTULOS = {
  idle: "",
  salvando: "Salvando…",
  salvo: "Salvo",
  erro: "Erro ao salvar",
};

export default function EstadoSalvamento({ estado }) {
  if (!estado || estado === "idle") return null;

  return (
    <span className={`caderno-save-status caderno-save-status--${estado}`}>
      {estado === "salvando" && <Loader2 size={14} className="spin" />}
      {estado === "salvo" && <Check size={14} />}
      {estado === "erro" && <AlertCircle size={14} />}
      {ROTULOS[estado]}
    </span>
  );
}
