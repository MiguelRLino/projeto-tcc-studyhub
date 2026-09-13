import { useCallback, useEffect, useMemo, useState } from "react";
import {
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  Clock,
  Flag,
  Plus,
  Trash2,
} from "lucide-react";
import { extrairMensagemErro } from "../services/api";
import {
  criarSessaoPlanejada,
  criarTarefa,
  excluirSessaoPlanejada,
  obterCalendario,
} from "../services/calendarioService";
import { listarDisciplinas } from "../services/disciplinasService";

const MESES = [
  "Janeiro",
  "Fevereiro",
  "Março",
  "Abril",
  "Maio",
  "Junho",
  "Julho",
  "Agosto",
  "Setembro",
  "Outubro",
  "Novembro",
  "Dezembro",
];

const DIAS_SEMANA = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"];

function isoHoje() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function gerarGradeCalendario(ano, mes) {
  const primeiro = new Date(ano, mes - 1, 1);
  let inicioSemana = (primeiro.getDay() + 6) % 7;
  const diasNoMes = new Date(ano, mes, 0).getDate();
  const diasMesAnterior = new Date(ano, mes - 1, 0).getDate();
  const celulas = [];

  for (let i = inicioSemana - 1; i >= 0; i -= 1) {
    const dia = diasMesAnterior - i;
    const m = mes === 1 ? 12 : mes - 1;
    const a = mes === 1 ? ano - 1 : ano;
    celulas.push({
      dia,
      foraMes: true,
      dataIso: `${a}-${String(m).padStart(2, "0")}-${String(dia).padStart(2, "0")}`,
    });
  }

  for (let dia = 1; dia <= diasNoMes; dia += 1) {
    celulas.push({
      dia,
      foraMes: false,
      dataIso: `${ano}-${String(mes).padStart(2, "0")}-${String(dia).padStart(2, "0")}`,
    });
  }

  let proximo = 1;
  while (celulas.length % 7 !== 0) {
    const m = mes === 12 ? 1 : mes + 1;
    const a = mes === 12 ? ano + 1 : ano;
    celulas.push({
      dia: proximo,
      foraMes: true,
      dataIso: `${a}-${String(m).padStart(2, "0")}-${String(proximo).padStart(2, "0")}`,
    });
    proximo += 1;
  }

  return celulas;
}

function formatarDataBr(iso) {
  if (!iso) return "—";
  const [y, m, d] = String(iso).slice(0, 10).split("-");
  if (!y || !m || !d) return "—";
  return `${d.padStart(2, "0")}/${m.padStart(2, "0")}/${y}`;
}

export default function CalendarioPage() {
  const hojeIso = isoHoje();
  const [hoje] = useState(() => new Date());
  const [ano, setAno] = useState(hoje.getFullYear());
  const [mes, setMes] = useState(hoje.getMonth() + 1);
  const [dados, setDados] = useState(null);
  const [disciplinas, setDisciplinas] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [diaSelecionado, setDiaSelecionado] = useState(hojeIso);
  const [modal, setModal] = useState(null);
  const [salvando, setSalvando] = useState(false);

  const [formTipo, setFormTipo] = useState("tarefa");
  const [formDisciplina, setFormDisciplina] = useState("");
  const [formDescricao, setFormDescricao] = useState("");
  const [formHora, setFormHora] = useState("");
  const [formDuracao, setFormDuracao] = useState("60");
  const [formObservacao, setFormObservacao] = useState("");

  const carregar = useCallback(async () => {
    setErro("");
    setCarregando(true);
    try {
      const [resCal, resDisc] = await Promise.all([
        obterCalendario(ano, mes),
        listarDisciplinas(),
      ]);
      setDados(resCal.data);
      const discs = Array.isArray(resDisc.data)
        ? resDisc.data
        : resDisc.data?.results ?? [];
      setDisciplinas(discs);
      setFormDisciplina((atual) => {
        if (atual && discs.some((d) => String(d.id_disciplina) === atual)) return atual;
        return discs.length ? String(discs[0].id_disciplina) : "";
      });
    } catch (e) {
      setErro(extrairMensagemErro(e));
    } finally {
      setCarregando(false);
    }
  }, [ano, mes]);

  useEffect(() => {
    carregar();
  }, [carregar]);

  const feriadosMap = useMemo(() => {
    const map = new Map();
    (dados?.feriados ?? []).forEach((f) => map.set(f.data, f));
    return map;
  }, [dados]);

  const eventosPorDia = useMemo(() => {
    const map = new Map();
    const add = (data, tipo, item) => {
      if (!data) return;
      if (!map.has(data)) {
        map.set(data, { tarefas: [], sessoesPlanejadas: [], sessoesRealizadas: [] });
      }
      map.get(data)[tipo].push(item);
    };
    (dados?.tarefas ?? []).forEach((t) => add(t.data_entrega, "tarefas", t));
    (dados?.sessoes_planejadas ?? []).forEach((s) =>
      add(s.data_planejada, "sessoesPlanejadas", s)
    );
    (dados?.sessoes_realizadas ?? []).forEach((s) =>
      add(s.data_sessao, "sessoesRealizadas", s)
    );
    return map;
  }, [dados]);

  const grade = useMemo(() => gerarGradeCalendario(ano, mes), [ano, mes]);

  const eventosDiaSelecionado = eventosPorDia.get(diaSelecionado) ?? {
    tarefas: [],
    sessoesPlanejadas: [],
    sessoesRealizadas: [],
  };
  const feriadoSelecionado = feriadosMap.get(diaSelecionado);

  function mudarMes(delta) {
    let novoMes = mes + delta;
    let novoAno = ano;
    if (novoMes < 1) {
      novoMes = 12;
      novoAno -= 1;
    } else if (novoMes > 12) {
      novoMes = 1;
      novoAno += 1;
    }
    setMes(novoMes);
    setAno(novoAno);
  }

  function irParaHoje() {
    setAno(hoje.getFullYear());
    setMes(hoje.getMonth() + 1);
    setDiaSelecionado(hojeIso);
  }

  function abrirModal(dataIso) {
    setDiaSelecionado(dataIso);
    setFormTipo("tarefa");
    setFormDescricao("");
    setFormHora("");
    setFormDuracao("60");
    setFormObservacao("");
    setModal({ dataIso });
  }

  async function salvarEvento(e) {
    e.preventDefault();
    if (!formDisciplina || !modal?.dataIso) return;
    setSalvando(true);
    setErro("");
    try {
      if (formTipo === "tarefa") {
        await criarTarefa({
          id_disciplina: Number(formDisciplina),
          descricao: formDescricao,
          data_entrega: modal.dataIso,
          hora_entrega: formHora ? `${formHora}:00` : null,
          status_tarefa: "pendente",
        });
      } else {
        await criarSessaoPlanejada({
          id_disciplina: Number(formDisciplina),
          data_planejada: modal.dataIso,
          duracao_prevista_minutos: formDuracao ? Number(formDuracao) : null,
          observacao: formObservacao,
        });
      }
      setModal(null);
      await carregar();
    } catch (err) {
      setErro(extrairMensagemErro(err));
    } finally {
      setSalvando(false);
    }
  }

  async function removerSessaoPlanejada(id) {
    setErro("");
    try {
      await excluirSessaoPlanejada(id);
      await carregar();
    } catch (err) {
      setErro(extrairMensagemErro(err));
    }
  }

  function contarEventos(dataIso) {
    const ev = eventosPorDia.get(dataIso);
    if (!ev) return 0;
    return ev.tarefas.length + ev.sessoesPlanejadas.length + ev.sessoesRealizadas.length;
  }

  return (
    <>
      <header className="shell-page-head shell-cal-head">
        <div>
          <h1>Calendário de Estudo</h1>
          <p>Tarefas, sessões planejadas e feriados do mês</p>
        </div>
        <div className="shell-cal-nav">
          <button type="button" className="shell-cal-nav-btn" onClick={() => mudarMes(-1)} aria-label="Mês anterior">
            <ChevronLeft size={20} />
          </button>
          <strong className="shell-cal-mes-titulo">
            {MESES[mes - 1]} {ano}
          </strong>
          <button type="button" className="shell-cal-nav-btn" onClick={() => mudarMes(1)} aria-label="Próximo mês">
            <ChevronRight size={20} />
          </button>
          <button type="button" className="shell-cal-hoje-btn" onClick={irParaHoje}>
            Hoje
          </button>
        </div>
      </header>

      {erro ? (
        <div className="shell-alert" role="alert">
          {erro}
        </div>
      ) : null}

      <div className="shell-cal-legenda" aria-label="Legenda">
        <span><i className="shell-cal-dot shell-cal-dot--tarefa" /> Tarefa</span>
        <span><i className="shell-cal-dot shell-cal-dot--planejada" /> Sessão planejada</span>
        <span><i className="shell-cal-dot shell-cal-dot--realizada" /> Sessão realizada</span>
        <span><i className="shell-cal-dot shell-cal-dot--feriado" /> Feriado</span>
      </div>

      <div className="shell-cal-layout">
        <section className="shell-cal-grid-wrap" aria-label="Calendário mensal">
          <div className="shell-cal-weekdays">
            {DIAS_SEMANA.map((d) => (
              <span key={d}>{d}</span>
            ))}
          </div>

          {carregando ? (
            <p className="shell-empty shell-cal-loading">Carregando calendário…</p>
          ) : (
            <div className="shell-cal-grid">
              {grade.map((celula) => {
                const feriado = feriadosMap.get(celula.dataIso);
                const ev = eventosPorDia.get(celula.dataIso);
                const total = contarEventos(celula.dataIso);
                const isHoje = celula.dataIso === hojeIso;
                const isSelected = celula.dataIso === diaSelecionado;
                const preview = [];
                if (ev?.tarefas?.length) preview.push({ tipo: "tarefa", label: ev.tarefas[0].descricao });
                if (ev?.sessoesPlanejadas?.length) {
                  preview.push({
                    tipo: "planejada",
                    label: ev.sessoesPlanejadas[0].disciplina_nome || "Sessão",
                  });
                }
                if (ev?.sessoesRealizadas?.length) {
                  preview.push({
                    tipo: "realizada",
                    label: ev.sessoesRealizadas[0].disciplina_nome || "Estudo",
                  });
                }

                return (
                  <button
                    key={celula.dataIso}
                    type="button"
                    className={[
                      "shell-cal-cell",
                      celula.foraMes ? "is-outside" : "",
                      isHoje ? "is-today" : "",
                      isSelected ? "is-selected" : "",
                      feriado ? "is-holiday" : "",
                    ]
                      .filter(Boolean)
                      .join(" ")}
                    onClick={() => setDiaSelecionado(celula.dataIso)}
                    onDoubleClick={() => !celula.foraMes && abrirModal(celula.dataIso)}
                  >
                    <span className="shell-cal-cell-day">{celula.dia}</span>
                    {feriado ? (
                      <span className="shell-cal-cell-holiday" title={feriado.nome}>
                        <Flag size={10} aria-hidden />
                        {feriado.nome.length > 14
                          ? `${feriado.nome.slice(0, 12)}…`
                          : feriado.nome}
                      </span>
                    ) : null}
                    <div className="shell-cal-cell-events">
                      {preview.slice(0, 2).map((p, idx) => (
                        <span
                          key={`${p.tipo}-${idx}`}
                          className={`shell-cal-pill shell-cal-pill--${p.tipo}`}
                        >
                          {p.label}
                        </span>
                      ))}
                      {total > 2 ? (
                        <span className="shell-cal-pill shell-cal-pill--more">+{total - 2}</span>
                      ) : null}
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </section>

        <aside className="shell-cal-detail">
          <div className="shell-cal-detail-head">
            <div>
              <h2>{formatarDataBr(diaSelecionado)}</h2>
              {feriadoSelecionado ? (
                <p className="shell-cal-detail-holiday">
                  <Flag size={14} aria-hidden />
                  {feriadoSelecionado.nome}
                </p>
              ) : (
                <p className="shell-cal-detail-sub">Detalhes do dia</p>
              )}
            </div>
            <button
              type="button"
              className="shell-cal-add-btn"
              onClick={() => abrirModal(diaSelecionado)}
              disabled={disciplinas.length === 0}
            >
              <Plus size={16} />
              Adicionar
            </button>
          </div>

          <div className="shell-cal-detail-section">
            <h3>
              <CalendarDays size={16} />
              Tarefas
            </h3>
            {eventosDiaSelecionado.tarefas.length === 0 ? (
              <p className="shell-cal-empty">Nenhuma tarefa neste dia.</p>
            ) : (
              <ul className="shell-cal-list">
                {eventosDiaSelecionado.tarefas.map((t) => (
                  <li key={t.id_tarefa} className="shell-cal-list-item shell-cal-list-item--tarefa">
                    <strong>{t.descricao}</strong>
                    <span>{t.disciplina_nome}</span>
                    {t.concluida ? <em className="shell-cal-tag">Concluída</em> : null}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="shell-cal-detail-section">
            <h3>
              <Clock size={16} />
              Sessões planejadas
            </h3>
            {eventosDiaSelecionado.sessoesPlanejadas.length === 0 ? (
              <p className="shell-cal-empty">Nenhuma sessão planejada.</p>
            ) : (
              <ul className="shell-cal-list">
                {eventosDiaSelecionado.sessoesPlanejadas.map((s) => (
                  <li
                    key={s.id_sessao_planejada}
                    className="shell-cal-list-item shell-cal-list-item--planejada"
                  >
                    <div>
                      <strong>{s.disciplina_nome || "Disciplina"}</strong>
                      {s.duracao_prevista_minutos ? (
                        <span>{s.duracao_prevista_minutos} min previstos</span>
                      ) : null}
                      {s.observacao ? <span>{s.observacao}</span> : null}
                    </div>
                    <button
                      type="button"
                      className="shell-cal-remove"
                      onClick={() => removerSessaoPlanejada(s.id_sessao_planejada)}
                      aria-label="Remover sessão planejada"
                    >
                      <Trash2 size={14} />
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="shell-cal-detail-section">
            <h3>Sessões realizadas</h3>
            {eventosDiaSelecionado.sessoesRealizadas.length === 0 ? (
              <p className="shell-cal-empty">Nenhuma sessão registrada.</p>
            ) : (
              <ul className="shell-cal-list">
                {eventosDiaSelecionado.sessoesRealizadas.map((s) => (
                  <li
                    key={s.id_sessao_estudo}
                    className="shell-cal-list-item shell-cal-list-item--realizada"
                  >
                    <strong>{s.disciplina_nome || "Disciplina"}</strong>
                    <span>{Number(s.tempo_estudo).toFixed(1)}h de estudo</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </aside>
      </div>

      {modal ? (
        <div className="shell-modal-overlay" role="presentation" onClick={() => setModal(null)}>
          <div
            className="shell-modal shell-cal-modal"
            role="dialog"
            aria-labelledby="cal-modal-title"
            onClick={(ev) => ev.stopPropagation()}
          >
            <h2 id="cal-modal-title">Novo evento — {formatarDataBr(modal.dataIso)}</h2>
            <form onSubmit={salvarEvento}>
              <div className="shell-cal-form-tabs">
                <button
                  type="button"
                  className={formTipo === "tarefa" ? "is-active" : ""}
                  onClick={() => setFormTipo("tarefa")}
                >
                  Tarefa
                </button>
                <button
                  type="button"
                  className={formTipo === "sessao" ? "is-active" : ""}
                  onClick={() => setFormTipo("sessao")}
                >
                  Sessão planejada
                </button>
              </div>

              <label htmlFor="cal-disciplina">Disciplina</label>
              <select
                id="cal-disciplina"
                value={formDisciplina}
                onChange={(e) => setFormDisciplina(e.target.value)}
                required
              >
                {disciplinas.length === 0 ? (
                  <option value="">Cadastre uma disciplina primeiro</option>
                ) : (
                  disciplinas.map((d) => (
                    <option key={d.id_disciplina} value={d.id_disciplina}>
                      {d.nome}
                    </option>
                  ))
                )}
              </select>

              {formTipo === "tarefa" ? (
                <>
                  <label htmlFor="cal-descricao">Descrição da tarefa</label>
                  <input
                    id="cal-descricao"
                    value={formDescricao}
                    onChange={(e) => setFormDescricao(e.target.value)}
                    required
                    maxLength={255}
                    placeholder="Ex.: Entregar lista de exercícios"
                  />
                  <label htmlFor="cal-hora">Horário de entrega (opcional)</label>
                  <input
                    id="cal-hora"
                    type="time"
                    value={formHora}
                    onChange={(e) => setFormHora(e.target.value)}
                  />
                </>
              ) : (
                <>
                  <label htmlFor="cal-duracao">Duração prevista (minutos)</label>
                  <input
                    id="cal-duracao"
                    type="number"
                    min={1}
                    max={1440}
                    value={formDuracao}
                    onChange={(e) => setFormDuracao(e.target.value)}
                  />
                  <label htmlFor="cal-obs">Observação (opcional)</label>
                  <input
                    id="cal-obs"
                    value={formObservacao}
                    onChange={(e) => setFormObservacao(e.target.value)}
                    maxLength={255}
                    placeholder="Ex.: Revisar capítulo 3"
                  />
                </>
              )}

              <div className="shell-modal-actions">
                <button type="button" className="shell-btn-ghost" onClick={() => setModal(null)}>
                  Cancelar
                </button>
                <button type="submit" className="shell-btn-primary" disabled={salvando || !formDisciplina}>
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
