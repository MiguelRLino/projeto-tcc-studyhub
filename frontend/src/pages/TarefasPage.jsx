import { useCallback, useEffect, useMemo, useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  CheckSquare,
  Circle,
  Clock,
  ListTodo,
  Pencil,
  Plus,
  Trash2,
} from "lucide-react";
import { extrairMensagemErro } from "../services/api";
import { listarDisciplinas } from "../services/disciplinasService";
import {
  atualizarTarefa,
  criarTarefa,
  excluirTarefaLogico,
  listarTarefas,
} from "../services/tarefasService";

const CARD_COLORS = ["#3b82f6", "#8b5cf6", "#22c55e", "#fb923c", "#eab308", "#ec4899"];

const FILTROS = [
  { id: "todas", label: "Todas" },
  { id: "pendentes", label: "Pendentes" },
  { id: "concluidas", label: "Concluídas" },
];

const STATUS_OPCOES = [
  { value: "pendente", label: "Pendente" },
  { value: "concluida", label: "Concluída" },
];

function corDisciplina(id, mapa) {
  if (id == null) return CARD_COLORS[0];
  const idx = mapa.get(id);
  return CARD_COLORS[(idx ?? id) % CARD_COLORS.length];
}

function formatarData(iso) {
  if (!iso) return "Sem prazo";
  const [ano, mes, dia] = iso.split("-");
  if (!ano || !mes || !dia) return iso;
  return `${dia}/${mes}/${ano}`;
}

function formatarHora(hora) {
  if (!hora) return "";
  const partes = hora.split(":");
  if (partes.length < 2) return hora;
  return `${partes[0]}:${partes[1]}`;
}

function horaParaInput(hora) {
  if (!hora) return "";
  return formatarHora(hora);
}

function formatarDataEntrega(data, hora) {
  const dataFmt = formatarData(data);
  if (dataFmt === "Sem prazo") return dataFmt;
  const horaFmt = formatarHora(hora);
  return horaFmt ? `${dataFmt} às ${horaFmt}` : dataFmt;
}

function rotuloStatus(tarefa) {
  if (tarefa.concluida) {
    return { classe: "concluida", label: "Concluída", Icon: CheckCircle2 };
  }
  if (tarefa.atrasada) {
    return { classe: "atrasada", label: "Atrasada", Icon: AlertCircle };
  }
  return { classe: "pendente", label: "Pendente", Icon: Clock };
}

export default function TarefasPage() {
  const [lista, setLista] = useState([]);
  const [disciplinas, setDisciplinas] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [filtro, setFiltro] = useState("todas");
  const [modal, setModal] = useState(null);
  const [formDescricao, setFormDescricao] = useState("");
  const [formDisciplina, setFormDisciplina] = useState("");
  const [formData, setFormData] = useState("");
  const [formHora, setFormHora] = useState("");
  const [formStatus, setFormStatus] = useState("pendente");
  const [salvando, setSalvando] = useState(false);

  const mapaDisciplinas = useMemo(() => {
    const mapa = new Map();
    disciplinas.forEach((d, idx) => mapa.set(d.id_disciplina, idx));
    return mapa;
  }, [disciplinas]);

  const carregar = useCallback(async () => {
    setErro("");
    try {
      const [resTarefas, resDisc] = await Promise.all([listarTarefas(), listarDisciplinas()]);
      const tarefas = Array.isArray(resTarefas.data)
        ? resTarefas.data
        : resTarefas.data?.results ?? [];
      const discs = Array.isArray(resDisc.data) ? resDisc.data : resDisc.data?.results ?? [];
      setLista(tarefas);
      setDisciplinas(discs);
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
    const concluidas = lista.filter((t) => t.concluida).length;
    const atrasadas = lista.filter((t) => t.atrasada).length;
    const pendentes = total - concluidas;
    return { total, concluidas, atrasadas, pendentes };
  }, [lista]);

  const listaFiltrada = useMemo(() => {
    if (filtro === "pendentes") return lista.filter((t) => !t.concluida);
    if (filtro === "concluidas") return lista.filter((t) => t.concluida);
    return lista;
  }, [lista, filtro]);

  function abrirCriar() {
    setFormDescricao("");
    setFormDisciplina(disciplinas[0]?.id_disciplina ? String(disciplinas[0].id_disciplina) : "");
    setFormData("");
    setFormHora("");
    setFormStatus("pendente");
    setModal({ modo: "criar" });
  }

  function abrirEditar(t) {
    setFormDescricao(t.descricao ?? "");
    setFormDisciplina(t.id_disciplina != null ? String(t.id_disciplina) : "");
    setFormData(t.data_entrega ?? "");
    setFormHora(horaParaInput(t.hora_entrega));
    setFormStatus(t.concluida ? "concluida" : "pendente");
    setModal({ modo: "editar", tarefa: t });
  }

  function fecharModal() {
    if (!salvando) setModal(null);
  }

  async function handleSalvar(e) {
    e.preventDefault();
    if (!formDisciplina) {
      setErro("Selecione uma disciplina para a tarefa.");
      return;
    }
    setSalvando(true);
    setErro("");
    try {
      const payload = {
        id_disciplina: Number(formDisciplina),
        descricao: formDescricao.trim(),
        data_entrega: formData || null,
        hora_entrega: formHora ? `${formHora}:00` : null,
        status_tarefa: formStatus,
      };
      if (modal.modo === "criar") {
        await criarTarefa(payload);
      } else {
        await atualizarTarefa(modal.tarefa.id_tarefa, payload);
      }
      setModal(null);
      await carregar();
    } catch (err) {
      setErro(extrairMensagemErro(err));
    } finally {
      setSalvando(false);
    }
  }

  async function handleExcluir(t) {
    const ok = window.confirm(
      `Excluir a tarefa "${t.descricao}"?\n\nA exclusão é lógica: ela some da lista mas permanece no histórico.`,
    );
    if (!ok) return;
    setErro("");
    try {
      await excluirTarefaLogico(t.id_tarefa);
      await carregar();
    } catch (err) {
      setErro(extrairMensagemErro(err));
    }
  }

  async function alternarConclusao(t) {
    setErro("");
    try {
      await atualizarTarefa(t.id_tarefa, {
        status_tarefa: t.concluida ? "pendente" : "concluida",
      });
      await carregar();
    } catch (err) {
      setErro(extrairMensagemErro(err));
    }
  }

  return (
    <>
      <div className="shell-disc-head">
        <header className="shell-page-head">
          <h1>Tarefas</h1>
          <p>Gerencie suas tarefas, prazos e entregas</p>
        </header>
        <button
          type="button"
          className="shell-btn-primary"
          onClick={abrirCriar}
          disabled={disciplinas.length === 0 && !carregando}
          title={disciplinas.length === 0 ? "Cadastre uma disciplina primeiro" : undefined}
        >
          <Plus size={18} aria-hidden />
          Nova Tarefa
        </button>
      </div>

      {erro ? (
        <div className="shell-alert" role="alert">
          {erro}
        </div>
      ) : null}

      <section className="shell-disc-stats" aria-label="Resumo das tarefas">
        <article className="shell-stat-card shell-stat-card--disc">
          <div className="shell-stat-icon-disc" aria-hidden>
            <ListTodo size={20} color="#93c5fd" />
          </div>
          <h3>Total de Tarefas</h3>
          <p className="value">{carregando ? "…" : resumo.total}</p>
        </article>

        <article className="shell-stat-card shell-stat-card--disc">
          <div className="shell-stat-icon-disc success" aria-hidden>
            <CheckCircle2 size={20} />
          </div>
          <h3>Concluídas</h3>
          <p className="value">{carregando ? "…" : resumo.concluidas}</p>
          <p className="hint">{resumo.pendentes} pendentes</p>
        </article>

        <article className="shell-stat-card shell-stat-card--disc">
          <div className="shell-stat-icon-disc danger" aria-hidden>
            <AlertCircle size={20} />
          </div>
          <h3>Em atraso</h3>
          <p className="value">{carregando ? "…" : resumo.atrasadas}</p>
          <p className="hint">Prazo vencido</p>
        </article>
      </section>

      <div className="shell-task-filters" role="tablist" aria-label="Filtrar tarefas">
        {FILTROS.map((f) => (
          <button
            key={f.id}
            type="button"
            role="tab"
            aria-selected={filtro === f.id}
            className={filtro === f.id ? "is-active" : undefined}
            onClick={() => setFiltro(f.id)}
          >
            {f.label}
          </button>
        ))}
      </div>

      {carregando ? (
        <p className="shell-empty">Carregando tarefas…</p>
      ) : disciplinas.length === 0 ? (
        <p className="shell-empty">
          Cadastre ao menos uma disciplina antes de criar tarefas.
        </p>
      ) : listaFiltrada.length === 0 ? (
        <p className="shell-empty">
          {filtro === "todas"
            ? 'Nenhuma tarefa cadastrada. Use "Nova Tarefa" para começar.'
            : "Nenhuma tarefa neste filtro."}
        </p>
      ) : (
        <div className="shell-disc-grid">
          {listaFiltrada.map((t) => {
            const { classe, label, Icon } = rotuloStatus(t);
            const cor = corDisciplina(t.id_disciplina, mapaDisciplinas);
            return (
              <article
                key={t.id_tarefa}
                className={`shell-disc-card shell-task-card${t.concluida ? " shell-task-card--done" : ""}`}
              >
                <div className="shell-disc-card-top">
                  <div
                    className="shell-disc-card-icon"
                    style={{ background: cor }}
                    aria-hidden
                  >
                    <CheckSquare size={22} strokeWidth={2} />
                  </div>
                  <div className="shell-disc-card-title">
                    <h3>{t.descricao}</h3>
                    <div className={`shell-task-status ${classe}`}>
                      <Icon size={15} strokeWidth={2.5} aria-hidden />
                      {label}
                    </div>
                  </div>
                  <button
                    type="button"
                    className={`shell-task-check${t.concluida ? " is-done" : ""}`}
                    onClick={() => alternarConclusao(t)}
                    title={t.concluida ? "Marcar como pendente" : "Marcar como concluída"}
                    aria-label={t.concluida ? "Marcar como pendente" : "Marcar como concluída"}
                  >
                    {t.concluida ? <CheckCircle2 size={22} /> : <Circle size={22} />}
                  </button>
                </div>

                <div className="shell-disc-metrics">
                  <div className="shell-disc-metric">
                    <span>Disciplina</span>
                    <strong>{t.disciplina_nome || "—"}</strong>
                  </div>
                  <div className="shell-disc-metric">
                    <span>Data de entrega</span>
                    <strong className={t.atrasada ? "shell-task-late" : undefined}>
                      {formatarDataEntrega(t.data_entrega, t.hora_entrega)}
                    </strong>
                  </div>
                </div>

                <div className="shell-disc-card-footer">
                  <button type="button" onClick={() => abrirEditar(t)}>
                    <Pencil size={16} aria-hidden />
                    Editar
                  </button>
                  <button type="button" className="shell-disc-del" onClick={() => handleExcluir(t)}>
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
          aria-labelledby="modal-tarefa-titulo"
          onClick={(ev) => {
            if (ev.target === ev.currentTarget) fecharModal();
          }}
        >
          <div className="shell-modal">
            <h2 id="modal-tarefa-titulo">
              {modal.modo === "criar" ? "Nova tarefa" : "Editar tarefa"}
            </h2>
            <form onSubmit={handleSalvar}>
              <div className="shell-field">
                <label htmlFor="tar-descricao">Descrição</label>
                <input
                  id="tar-descricao"
                  value={formDescricao}
                  onChange={(e) => setFormDescricao(e.target.value)}
                  placeholder="Ex.: Resolver lista de exercícios"
                  required
                  maxLength={255}
                  autoFocus
                />
              </div>
              <div className="shell-field">
                <label htmlFor="tar-disciplina">Disciplina</label>
                <select
                  id="tar-disciplina"
                  value={formDisciplina}
                  onChange={(e) => setFormDisciplina(e.target.value)}
                  required
                >
                  <option value="">Selecione…</option>
                  {disciplinas.map((d) => (
                    <option key={d.id_disciplina} value={d.id_disciplina}>
                      {d.nome}
                    </option>
                  ))}
                </select>
              </div>
              <div className="shell-field-row">
                <div className="shell-field">
                  <label htmlFor="tar-data">Data de entrega</label>
                  <input
                    id="tar-data"
                    type="date"
                    value={formData}
                    onChange={(e) => {
                      const val = e.target.value;
                      setFormData(val);
                      if (!val) setFormHora("");
                    }}
                  />
                </div>
                <div className="shell-field">
                  <label htmlFor="tar-hora">Horário</label>
                  <input
                    id="tar-hora"
                    type="time"
                    value={formHora}
                    onChange={(e) => setFormHora(e.target.value)}
                    disabled={!formData}
                    title={formData ? undefined : "Informe a data de entrega primeiro"}
                  />
                </div>
              </div>
              <p className="shell-field-hint">
                O horário é opcional e melhora o aviso de 2 horas no Telegram.
              </p>
              <div className="shell-field">
                <label htmlFor="tar-status">Status</label>
                <select
                  id="tar-status"
                  value={formStatus}
                  onChange={(e) => setFormStatus(e.target.value)}
                >
                  {STATUS_OPCOES.map((o) => (
                    <option key={o.value} value={o.value}>
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
