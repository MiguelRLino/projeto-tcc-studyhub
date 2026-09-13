import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { BookOpen, Calendar, Circle, Clock, Play } from "lucide-react";
import { extrairMensagemErro } from "../services/api";
import { listarDisciplinas } from "../services/disciplinasService";
import {
  criarSessao,
  listarSessoes,
  obterResumoSessoes,
} from "../services/sessoesService";

const CORES_DISCIPLINA = ["#3b82f6", "#8b5cf6", "#22c55e", "#fb923c", "#ec4899"];

function formatarCronometro(segundos) {
  const h = Math.floor(segundos / 3600);
  const m = Math.floor((segundos % 3600) / 60);
  const s = segundos % 60;
  return [h, m, s].map((n) => String(n).padStart(2, "0")).join(":");
}

function formatarDataBr(iso) {
  if (!iso) return "—";
  const [y, m, d] = String(iso).slice(0, 10).split("-");
  if (!y || !m || !d) return "—";
  return `${d.padStart(2, "0")}/${m.padStart(2, "0")}/${y}`;
}

/** Converte segundos em horas (máx. 2 casas decimais, como no banco). */
function segundosParaHoras(segundos) {
  const horas = Math.round((segundos / 3600) * 100) / 100;
  if (horas <= 0 && segundos > 0) return 0.01;
  return horas;
}

function corDisciplina(idDisciplina, mapa) {
  const idx = mapa.get(idDisciplina);
  return CORES_DISCIPLINA[(idx ?? 0) % CORES_DISCIPLINA.length];
}

export default function SessoesEstudoPage() {
  const [resumo, setResumo] = useState(null);
  const [historico, setHistorico] = useState([]);
  const [disciplinas, setDisciplinas] = useState([]);
  const [disciplinaId, setDisciplinaId] = useState("");
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [rodando, setRodando] = useState(false);
  const [segundos, setSegundos] = useState(0);
  const [salvando, setSalvando] = useState(false);
  const inicioRef = useRef(null);
  const intervalRef = useRef(null);

  const mapaCores = useMemo(() => {
    const m = new Map();
    disciplinas.forEach((d, i) => m.set(d.id_disciplina, i));
    return m;
  }, [disciplinas]);

  const carregar = useCallback(async () => {
    setErro("");
    try {
      const [resResumo, resLista, resDisc] = await Promise.all([
        obterResumoSessoes(),
        listarSessoes(),
        listarDisciplinas(),
      ]);
      const discs = Array.isArray(resDisc.data)
        ? resDisc.data
        : resDisc.data?.results ?? [];
      setResumo(resResumo.data);
      setHistorico(Array.isArray(resLista.data) ? resLista.data : resLista.data?.results ?? []);
      setDisciplinas(discs);
      setDisciplinaId((atual) => {
        if (atual && discs.some((d) => String(d.id_disciplina) === atual)) return atual;
        return discs.length ? String(discs[0].id_disciplina) : "";
      });
    } catch (e) {
      setErro(extrairMensagemErro(e));
    } finally {
      setCarregando(false);
    }
  }, []);

  useEffect(() => {
    carregar();
  }, [carregar]);

  useEffect(() => {
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  function iniciar() {
    if (rodando || !disciplinaId) return;
    setErro("");
    inicioRef.current = Date.now() - segundos * 1000;
    setRodando(true);
    intervalRef.current = setInterval(() => {
      const decorrido = Math.floor((Date.now() - inicioRef.current) / 1000);
      setSegundos(decorrido);
    }, 250);
  }

  function pararTimer() {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setRodando(false);
  }

  async function finalizar() {
    if (!rodando || segundos < 1) return;
    pararTimer();
    const horas = segundosParaHoras(segundos);
    if (horas <= 0) {
      setErro("Registre pelo menos alguns segundos de estudo.");
      setSegundos(0);
      return;
    }
    setSalvando(true);
    setErro("");
    try {
      await criarSessao({
        id_disciplina: Number(disciplinaId),
        tempo_estudo: horas,
      });
      setSegundos(0);
      inicioRef.current = null;
      setCarregando(true);
      await carregar();
    } catch (e) {
      setErro(extrairMensagemErro(e));
    } finally {
      setSalvando(false);
      setCarregando(false);
    }
  }

  const podeFinalizar = rodando && segundos >= 1 && !salvando;

  return (
    <>
      <header className="shell-page-head">
        <h1>Sessões de Estudo</h1>
        <p>Registre e acompanhe seu tempo de estudo</p>
      </header>

      {erro ? (
        <div className="shell-alert" role="alert">
          {erro}
        </div>
      ) : null}

      <section className="shell-sess-stats" aria-label="Resumo das sessões">
        <article className="shell-stat-card shell-stat-card--disc">
          <div className="shell-stat-icon-disc purple" aria-hidden>
            <Clock size={20} color="#a5b4fc" />
          </div>
          <h3>Total de Horas</h3>
          <p className="value">{carregando ? "…" : `${resumo?.total_horas ?? 0}h`}</p>
        </article>

        <article className="shell-stat-card shell-stat-card--disc">
          <div className="shell-stat-icon-disc green" aria-hidden>
            <Calendar size={20} color="#6ee7b7" />
          </div>
          <h3>Sessões Hoje</h3>
          <p className="value">{carregando ? "…" : resumo?.sessoes_hoje ?? 0}</p>
        </article>

        <article className="shell-stat-card shell-stat-card--disc">
          <div className="shell-stat-icon-disc purple" aria-hidden>
            <BookOpen size={20} color="#c4b5fd" />
          </div>
          <h3>Total de Sessões</h3>
          <p className="value">{carregando ? "…" : resumo?.total_sessoes ?? 0}</p>
        </article>
      </section>

      <div className="shell-sess-columns">
        <section className="shell-sess-panel shell-sess-cronometro">
          <h2>Cronômetro de Estudo</h2>

          <div className="shell-sess-timer-display" aria-live="polite">
            <span className="shell-sess-timer-value">{formatarCronometro(segundos)}</span>
            <span className="shell-sess-timer-label">Tempo decorrido</span>
          </div>

          <div className="shell-sess-field">
            <label htmlFor="sess-disciplina">Disciplina</label>
            <select
              id="sess-disciplina"
              value={disciplinaId}
              onChange={(e) => setDisciplinaId(e.target.value)}
              disabled={rodando || salvando || disciplinas.length === 0}
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
          </div>

          <div className="shell-sess-actions">
            <button
              type="button"
              className="shell-sess-btn-iniciar"
              onClick={iniciar}
              disabled={rodando || salvando || !disciplinaId}
            >
              <Play size={18} aria-hidden />
              Iniciar
            </button>
            <button
              type="button"
              className={`shell-sess-btn-finalizar${podeFinalizar ? " is-active" : ""}`}
              onClick={finalizar}
              disabled={!podeFinalizar}
            >
              <Circle size={16} aria-hidden />
              Finalizar
            </button>
          </div>
        </section>

        <section className="shell-sess-panel shell-sess-historico">
          <h2>Histórico de Sessões</h2>

          {carregando ? (
            <p className="shell-empty shell-sess-empty">Carregando…</p>
          ) : historico.length === 0 ? (
            <p className="shell-empty shell-sess-empty">
              Nenhuma sessão registrada ainda. Use o cronômetro para começar.
            </p>
          ) : (
            <ul className="shell-sess-list">
              {historico.map((s) => {
                const horas = Number(s.tempo_estudo) || 0;
                const minutos = Math.round(horas * 60);
                const cor = corDisciplina(s.id_disciplina, mapaCores);
                return (
                  <li key={s.id_sessao_estudo} className="shell-sess-list-item">
                    <div
                      className="shell-sess-list-icon"
                      style={{ background: cor }}
                      aria-hidden
                    >
                      <BookOpen size={18} strokeWidth={2} />
                    </div>
                    <div className="shell-sess-list-info">
                      <strong>{s.disciplina_nome || "Disciplina"}</strong>
                      <span>{formatarDataBr(s.data_sessao)}</span>
                    </div>
                    <div className="shell-sess-list-duracao">
                      <strong>{minutos} min</strong>
                      <span>{horas.toFixed(1)}h</span>
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
        </section>
      </div>
    </>
  );
}
