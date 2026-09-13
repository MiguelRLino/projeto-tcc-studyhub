const SUGESTOES = [
  {
    id: "explicar",
    label: "Explicar um conteúdo",
    texto: "Explique o conceito de chave estrangeira em banco de dados de forma simples.",
  },
  {
    id: "resumo",
    label: "Fazer resumo",
    texto: "Faça um resumo objetivo sobre normalização de banco de dados.",
  },
  {
    id: "perguntas",
    label: "Criar perguntas",
    texto: "Crie 5 perguntas de revisão sobre React Hooks para eu estudar.",
  },
  {
    id: "plano",
    label: "Montar plano de estudo",
    texto: "Monte um plano simples de estudo de 3 dias para revisar SQL básico.",
  },
];

export default function SugestoesRapidas({ onSelecionar, desabilitado }) {
  return (
    <div className="ia-sugestoes">
      <span className="ia-sugestoes-label">Sugestões rápidas</span>
      <div className="ia-sugestoes-lista">
        {SUGESTOES.map((s) => (
          <button
            key={s.id}
            type="button"
            className="ia-sugestao-btn"
            disabled={desabilitado}
            onClick={() => onSelecionar(s.texto)}
          >
            {s.label}
          </button>
        ))}
      </div>
    </div>
  );
}
