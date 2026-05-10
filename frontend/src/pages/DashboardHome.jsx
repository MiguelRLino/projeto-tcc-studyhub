import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { BookOpen, Calendar, CheckSquare, Clock } from "lucide-react";
import { extrairMensagemErro } from "../services/api";
import { obterResumoDashboard } from "../services/dashboardService";
import { obterAluno } from "../services/authService";
import { tempoRelativo } from "../utils/tempoRelativo";

export default function DashboardHome() {
  const aluno = obterAluno();
  const [dados, setDados] = useState(null);
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    let vivo = true;
    (async () => {
      try {
        const { data } = await obterResumoDashboard();
        if (vivo) setDados(data);
      } catch (e) {
        if (vivo) setErro(extrairMensagemErro(e));
      } finally {
        if (vivo) setCarregando(false);
      }
    })();
    return () => {
      vivo = false;
    };
  }, []);

  const grafico = dados?.grafico_horas_semana ?? [];

  return (
    <>
      <header className="shell-page-head">
        <h1>Dashboard</h1>
        <p>
          Bem-vindo de volta{aluno?.nome ? `, ${aluno.nome.split(" ")[0]}` : ""}! Aqui está um
          resumo das suas atividades.
        </p>
      </header>

      {erro ? (
        <div className="shell-alert" role="alert">
          {erro}
        </div>
      ) : null}

      <section className="shell-stats-grid">
        <article className="shell-stat-card">
          <CheckSquare className="shell-stat-icon" color="#60a5fa" size={22} />
          <h3>Tarefas pendentes</h3>
          <p className="value">{carregando ? "…" : dados?.tarefas_pendentes ?? 0}</p>
          <p className="hint">Na sua lista atual</p>
        </article>

        <article className="shell-stat-card">
          <Clock className="shell-stat-icon" color="#6366f1" size={22} />
          <h3>Horas estudadas</h3>
          <p className="value">
            {carregando ? "…" : `${Math.round(dados?.horas_estudadas_semana ?? 0)}h`}
          </p>
          <p className="hint up">Esta semana</p>
        </article>

        <article className="shell-stat-card">
          <BookOpen className="shell-stat-icon" color="#60a5fa" size={22} />
          <h3>Disciplinas ativas</h3>
          <p className="value">{carregando ? "…" : dados?.disciplinas_ativas ?? 0}</p>
          <p className="hint">
            {carregando
              ? "…"
              : `${dados?.disciplinas_prioridade_alta ?? 0} em alta prioridade`}
          </p>
        </article>

        <article className="shell-stat-card">
          <Calendar className="shell-stat-icon" color="#fb923c" size={22} />
          <h3>Próxima entrega</h3>
          <p className="value">
            {carregando
              ? "…"
              : dados?.proxima_entrega
                ? `${dados.proxima_entrega.dias} ${dados.proxima_entrega.dias === 1 ? "dia" : "dias"}`
                : "—"}
          </p>
          <p className="hint warn">
            {carregando
              ? ""
              : dados?.proxima_entrega
                ? `${dados.proxima_entrega.disciplina ? `${dados.proxima_entrega.disciplina} · ` : ""}${dados.proxima_entrega.titulo}`
                : "Sem tarefas com data futura"}
          </p>
        </article>
      </section>

      <div className="shell-columns">
        <section className="shell-panel">
          <h2>Horas de estudo</h2>
          <div style={{ width: "100%", height: 280 }}>
            <ResponsiveContainer>
              <BarChart data={grafico} margin={{ top: 8, right: 8, left: -18, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a2a35" vertical={false} />
                <XAxis dataKey="dia" tick={{ fill: "#9ca3af", fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis
                  tick={{ fill: "#9ca3af", fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                  allowDecimals
                  domain={[0, "auto"]}
                  label={{ value: "h", position: "insideLeft", fill: "#6b7280", fontSize: 11 }}
                />
                <Tooltip
                  contentStyle={{
                    background: "#16161e",
                    border: "1px solid rgba(255,255,255,0.08)",
                    borderRadius: 10,
                    color: "#f9fafb",
                  }}
                  formatter={(value) => [`${value} h`, "Horas"]}
                />
                <Bar dataKey="horas" fill="#6366f1" radius={[6, 6, 0, 0]} maxBarSize={40} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="shell-panel">
          <h2>Atividades recentes</h2>
          {carregando ? (
            <p className="shell-empty">Carregando…</p>
          ) : !dados?.atividades_recentes?.length ? (
            <p className="shell-empty">Nenhuma atividade registrada ainda.</p>
          ) : (
            <div className="shell-feed">
              {dados.atividades_recentes.map((item, i) => (
                <div key={`${item.quando}-${i}`} className="shell-feed-item">
                  <span className="shell-feed-dot" aria-hidden />
                  <div className="shell-feed-body">
                    <p>{item.descricao}</p>
                    <div className="shell-feed-meta">{tempoRelativo(item.quando)}</div>
                    {item.rotulo ? <span className="shell-tag">{item.rotulo}</span> : null}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </>
  );
}
