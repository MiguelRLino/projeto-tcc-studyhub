import { useCallback, useEffect, useMemo, useState } from "react";
import {
  BookOpen,
  Clock,
  Minus,
  Pencil,
  Plus,
  Trash2,
  TrendingDown,
  TrendingUp,
} from "lucide-react";
import { extrairMensagemErro } from "../services/api";
import {
  atualizarDisciplina,
  criarDisciplina,
  excluirDisciplinaLogico,
  listarDisciplinas,
} from "../services/disciplinasService";

const NIVEL_OPCOES = [
  { value: "", label: "Não informado" },
  { value: "1", label: "1 — Muito fácil" },
  { value: "2", label: "2 — Fácil" },
  { value: "3", label: "3 — Médio" },
  { value: "4", label: "4 — Difícil" },
  { value: "5", label: "5 — Muito difícil" },
];

const CARD_COLORS = ["#3b82f6", "#8b5cf6", "#22c55e", "#fb923c", "#eab308", "#ec4899"];

function tierDificuldade(nivel) {
  if (nivel == null || nivel === "") {
    return { classe: "neutra", label: "Sem nível", Icon: Minus };
  }
  const n = Number(nivel);
  if (n >= 4) return { classe: "alta", label: "Difícil", Icon: TrendingUp };
  if (n === 3) return { classe: "media", label: "Médio", Icon: Minus };
  return { classe: "facil", label: "Fácil", Icon: TrendingDown };
}

export default function DisciplinasPage() {
  const [lista, setLista] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [modal, setModal] = useState(null);
  const [formNome, setFormNome] = useState("");
  const [formNivel, setFormNivel] = useState("");
  const [salvando, setSalvando] = useState(false);

  const carregar = useCallback(async () => {
    setErro("");
    try {
      const { data } = await listarDisciplinas();
      setLista(Array.isArray(data) ? data : data?.results ?? []);
    } catch (e) {
      setErro(extrairMensagemErro(e));
    } finally {
      setCarregando(false);
    }
  }, []);

  useEffect(() => {
    carregar();
  }, [carregar]);

  const resumo = useMemo(() => {
    const total = lista.length;
    const alta = lista.filter((d) => (d.nivel_dificuldade ?? 0) >= 4).length;
    const horas = lista.reduce((acc, d) => acc + (Number(d.horas_estudadas) || 0), 0);
    return {
      total,
      alta,
      horas: Math.round(horas),
    };
  }, [lista]);

  function abrirCriar() {
    setFormNome("");
    setFormNivel("");
    setModal({ modo: "criar" });
  }

  function abrirEditar(d) {
    setFormNome(d.nome ?? "");
    setFormNivel(d.nivel_dificuldade != null ? String(d.nivel_dificuldade) : "");
    setModal({ modo: "editar", disciplina: d });
  }

  function fecharModal() {
    if (!salvando) setModal(null);
  }

  async function handleSalvar(e) {
    e.preventDefault();
    setSalvando(true);
    setErro("");
    try {
      const payload = {
        nome: formNome.trim(),
        nivel_dificuldade: formNivel === "" ? null : Number(formNivel),
      };
      if (modal.modo === "criar") {
        await criarDisciplina(payload);
      } else {
        await atualizarDisciplina(modal.disciplina.id_disciplina, payload);
      }
      setModal(null);
      await carregar();
    } catch (err) {
      setErro(extrairMensagemErro(err));
    } finally {
      setSalvando(false);
    }
  }

  async function handleExcluir(d) {
    const ok = window.confirm(
      `Excluir a disciplina "${d.nome}"?\n\nA exclusão é lógica: ela some da lista mas permanece no histórico do sistema.`,
    );
    if (!ok) return;
    setErro("");
    try {
      await excluirDisciplinaLogico(d.id_disciplina);
      await carregar();
    } catch (err) {
      setErro(extrairMensagemErro(err));
    }
  }

  return (
    <>
      <div className="shell-disc-head">
        <header className="shell-page-head">
          <h1>Disciplinas</h1>
          <p>Gerencie suas matérias e disciplinas</p>
        </header>
        <button type="button" className="shell-btn-primary" onClick={abrirCriar}>
          <Plus size={18} aria-hidden />
          Nova Disciplina
        </button>
      </div>

      {erro ? (
        <div className="shell-alert" role="alert">
          {erro}
        </div>
      ) : null}

      <section className="shell-disc-stats" aria-label="Resumo das disciplinas">
        <article className="shell-stat-card shell-stat-card--disc">
          <div className="shell-stat-icon-disc" aria-hidden>
            <BookOpen size={20} color="#93c5fd" />
          </div>
          <h3>Total de Disciplinas</h3>
          <p className="value">{carregando ? "…" : resumo.total}</p>
        </article>

        <article className="shell-stat-card shell-stat-card--disc">
          <div className="shell-stat-icon-disc danger" aria-hidden>
            <TrendingUp size={20} />
          </div>
          <h3>Dificuldade Alta</h3>
          <p className="value">{carregando ? "…" : resumo.alta}</p>
          <p className="hint">Nível 4 ou 5</p>
        </article>

        <article className="shell-stat-card shell-stat-card--disc">
          <div className="shell-stat-icon-disc" aria-hidden>
            <Clock size={20} color="#c4b5fd" />
          </div>
          <h3>Total de Horas</h3>
          <p className="value">{carregando ? "…" : `${resumo.horas}h`}</p>
          <p className="hint">Somatório das sessões por disciplina</p>
        </article>
      </section>

      {carregando ? (
        <p className="shell-empty">Carregando disciplinas…</p>
      ) : lista.length === 0 ? (
        <p className="shell-empty">
          Nenhuma disciplina cadastrada. Use &quot;Nova Disciplina&quot; para começar.
        </p>
      ) : (
        <div className="shell-disc-grid">
          {lista.map((d, idx) => {
            const { classe, label, Icon } = tierDificuldade(d.nivel_dificuldade);
            const cor = CARD_COLORS[idx % CARD_COLORS.length];
            const horas = Math.round(Number(d.horas_estudadas) || 0);
            const pendentes = Number(d.tarefas_pendentes) || 0;
            return (
              <article key={d.id_disciplina} className="shell-disc-card">
                <div className="shell-disc-card-top">
                  <div
                    className="shell-disc-card-icon"
                    style={{ background: cor }}
                    aria-hidden
                  >
                    <BookOpen size={22} strokeWidth={2} />
                  </div>
                  <div className="shell-disc-card-title">
                    <h3>{d.nome}</h3>
                    <div className={`shell-diff-row ${classe}`}>
                      <Icon size={16} strokeWidth={2.5} aria-hidden />
                      {label}
                    </div>
                  </div>
                </div>

                <div className="shell-disc-metrics">
                  <div className="shell-disc-metric">
                    <span>Horas estudadas</span>
                    <strong>{horas}h</strong>
                  </div>
                  <div className="shell-disc-metric">
                    <span>Tarefas pendentes</span>
                    <strong>{pendentes}</strong>
                  </div>
                </div>

                <div className="shell-disc-card-footer">
                  <button type="button" onClick={() => abrirEditar(d)}>
                    <Pencil size={16} aria-hidden />
                    Editar
                  </button>
                  <button type="button" className="shell-disc-del" onClick={() => handleExcluir(d)}>
                    <Trash2 size={16} aria-hidden />
                    Excluir
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      )}

      {modal ? (
        <div
          className="shell-modal-overlay"
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-disciplina-titulo"
          onClick={(ev) => {
            if (ev.target === ev.currentTarget) fecharModal();
          }}
        >
          <div className="shell-modal">
            <h2 id="modal-disciplina-titulo">
              {modal.modo === "criar" ? "Nova disciplina" : "Editar disciplina"}
            </h2>
            <form onSubmit={handleSalvar}>
              <div className="shell-field">
                <label htmlFor="disc-nome">Nome</label>
                <input
                  id="disc-nome"
                  value={formNome}
                  onChange={(e) => setFormNome(e.target.value)}
                  placeholder="Ex.: Matemática"
                  required
                  maxLength={100}
                  autoFocus
                />
              </div>
              <div className="shell-field">
                <label htmlFor="disc-nivel">Nível de dificuldade</label>
                <select
                  id="disc-nivel"
                  value={formNivel}
                  onChange={(e) => setFormNivel(e.target.value)}
                >
                  {NIVEL_OPCOES.map((o) => (
                    <option key={o.value || "empty"} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="shell-modal-actions">
                <button type="button" className="shell-btn-ghost" onClick={fecharModal} disabled={salvando}>
                  Cancelar
                </button>
                <button type="submit" className="shell-btn-primary" disabled={salvando}>
                  {salvando ? "Salvando…" : "Salvar"}
                </button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </>
  );
}
