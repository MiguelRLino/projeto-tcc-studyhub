import { Trash2 } from "lucide-react";

function rotuloGrupo(dataIso) {
  const data = new Date(dataIso);
  const hoje = new Date();
  const ontem = new Date();
  ontem.setDate(hoje.getDate() - 1);

  const fmt = (d) =>
    d.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric" });

  if (fmt(data) === fmt(hoje)) return "Hoje";
  if (fmt(data) === fmt(ontem)) return "Ontem";
  return data.toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function agruparPorData(itens) {
  const mapa = new Map();
  for (const item of itens) {
    const chave = rotuloGrupo(item.data_criacao);
    if (!mapa.has(chave)) mapa.set(chave, []);
    mapa.get(chave).push(item);
  }
  return mapa;
}

export default function HistoricoConversas({
  itens,
  selecionadaId,
  onSelecionar,
  onExcluir,
  carregando,
}) {
  if (carregando) {
    return <p className="ia-historico-vazio">Carregando histórico…</p>;
  }

  if (!itens?.length) {
    return (
      <p className="ia-historico-vazio">
        Nenhuma conversa ainda. Faça sua primeira pergunta!
      </p>
    );
  }

  const grupos = agruparPorData(itens);

  return (
    <div className="ia-historico">
      {[...grupos.entries()].map(([grupo, lista]) => (
        <div key={grupo} className="ia-historico-grupo">
          <h4>{grupo}</h4>
          <ul>
            {lista.map((item) => (
              <li key={item.id_conversa}>
                <button
                  type="button"
                  className={`ia-historico-item${
                    selecionadaId === item.id_conversa ? " is-active" : ""
                  }`}
                  onClick={() => onSelecionar(item)}
                >
                  {item.titulo || item.pergunta}
                </button>
                <button
                  type="button"
                  className="ia-historico-excluir"
                  title="Excluir conversa"
                  onClick={(e) => {
                    e.stopPropagation();
                    onExcluir(item.id_conversa);
                  }}
                >
                  <Trash2 size={14} />
                </button>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
