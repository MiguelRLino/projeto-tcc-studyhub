import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Award, Clock, Target, TrendingUp } from "lucide-react";
import { useCoresGrafico } from "../hooks/useTema";
import { extrairMensagemErro } from "../services/api";
import { obterResumoRelatorios } from "../services/relatoriosService";

const CORES_PIZZA = ["#6366f1", "#3b82f6", "#22c55e", "#fb923c", "#eab308", "#ec4899", "#14b8a6"];

const tooltipStyle = (chart) => ({
  background: chart.tooltipBg,
  border: `1px solid ${chart.tooltipBorder}`,
  borderRadius: 10,
  color: chart.tooltipColor,
});

export default function RelatoriosPage() {
  const chart = useCoresGrafico();
  const [dados, setDados] = useState(null);
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    let vivo = true;
    (async () => {
      try {
        const { data } = await obterResumoRelatorios();
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

  const distribuicao = dados?.distribuicao_disciplinas ?? [];
  const tempoDisciplinas = useMemo(
    () => [...(dados?.tempo_por_disciplina ?? [])].reverse(),
    [dados],
  );

  return (
    <>
      <header className="shell-page-head">
        <h1>Relatórios</h1>
        <p>Análise detalhada do seu desempenho nos estudos</p>
      </header>

      {erro ? (
        <div className="shell-alert" role="alert">
          {erro}
        </div>
      ) : null}

      <section className="shell-stats-grid" aria-label="Resumo de relatórios">
        <article className="shell-stat-card">
          <Clock className="shell-stat-icon" color="#6366f1" size={22} />
          <h3>Total de horas</h3>
          <p className="value">{carregando ? "…" : `${dados?.total_horas ?? 0}h`}</p>
          <p className="hint">Somatório de todas as sessões</p>
        </article>

        <article className="shell-stat-card">
          <TrendingUp className="shell-stat-icon" color="#34d399" size={22} />
          <h3>Média por disciplina</h3>
          <p className="value">{carregando ? "…" : `${dados?.media_por_disciplina ?? 0}h`}</p>
          <p className="hint">Horas totais ÷ disciplinas</p>
        </article>

        <article className="shell-stat-card">
          <Award className="shell-stat-icon" color="#fb923c" size={22} />
          <h3>Melhor disciplina</h3>
          <p className="value shell-relatorios-disc">
            {carregando ? "…" : dados?.melhor_disciplina ?? "—"}
          </p>
          <p className="hint">
            {carregando ? "…" : `${dados?.melhor_disciplina_horas ?? 0}h estudadas`}
          </p>
        </article>

        <article className="shell-stat-card">
          <Target className="shell-stat-icon" color="#a855f7" size={22} />
          <h3>Meta semanal</h3>
          <p className="value">{carregando ? "…" : `${dados?.meta_semanal_pct ?? 0}%`}</p>
          <p className="hint up">
            {carregando
              ? "…"
              : `${dados?.horas_estudadas_semana ?? 0}h de ${dados?.meta_semanal_horas ?? 10}h`}
          </p>
        </article>
      </section>

      <div className="shell-columns">
        <section className="shell-panel">
          <h2>Horas de estudo semanal</h2>
          <p className="shell-panel-sub">Distribuição por dia da semana atual</p>
          <div className="shell-chart-wrap">
            {carregando ? (
              <p className="shell-empty">Carregando…</p>
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart
                  data={dados?.grafico_horas_semana ?? []}
                  margin={{ top: 8, right: 8, left: -18, bottom: 0 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke={chart.grid} vertical={false} />
                  <XAxis
                    dataKey="dia"
                    tick={{ fill: chart.tick, fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fill: chart.tick, fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                    allowDecimals
                    domain={[0, "auto"]}
                  />
                  <Tooltip
                    contentStyle={tooltipStyle(chart)}
                    formatter={(value) => [`${value} h`, "Horas"]}
                  />
                  <Bar dataKey="horas" fill="#6366f1" radius={[6, 6, 0, 0]} maxBarSize={44} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </section>

        <section className="shell-panel">
          <h2>Distribuição por disciplina</h2>
          <p className="shell-panel-sub">Proporção do tempo de estudo por matéria</p>
          <div className="shell-chart-wrap">
            {carregando ? (
              <p className="shell-empty">Carregando…</p>
            ) : distribuicao.length === 0 ? (
              <p className="shell-empty">Registre sessões de estudo para ver o gráfico.</p>
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={distribuicao}
                    dataKey="horas"
                    nameKey="disciplina"
                    cx="50%"
                    cy="50%"
                    innerRadius={52}
                    outerRadius={92}
                    paddingAngle={2}
                  >
                    {distribuicao.map((_, i) => (
                      <Cell key={i} fill={CORES_PIZZA[i % CORES_PIZZA.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={tooltipStyle(chart)}
                    formatter={(value, _name, item) => [
                      `${value} h`,
                      item?.payload?.disciplina ?? "Disciplina",
                    ]}
                  />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
          {distribuicao.length > 0 ? (
            <ul className="shell-relatorios-legenda">
              {distribuicao.map((item, i) => (
                <li key={item.disciplina}>
                  <span
                    className="shell-relatorios-legenda-dot"
                    style={{ background: CORES_PIZZA[i % CORES_PIZZA.length] }}
                  />
                  {item.disciplina} ({item.horas}h)
                </li>
              ))}
            </ul>
          ) : null}
        </section>
      </div>

      <div className="shell-columns shell-relatorios-bottom">
        <section className="shell-panel">
          <h2>Evolução mensal</h2>
          <p className="shell-panel-sub">Progresso ao longo das semanas</p>
          <div className="shell-chart-wrap">
            {carregando ? (
              <p className="shell-empty">Carregando…</p>
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <LineChart
                  data={dados?.evolucao_semanal ?? []}
                  margin={{ top: 8, right: 8, left: -18, bottom: 0 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke={chart.grid} vertical={false} />
                  <XAxis
                    dataKey="semana"
                    tick={{ fill: chart.tick, fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fill: chart.tick, fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                    allowDecimals
                    domain={[0, "auto"]}
                  />
                  <Tooltip
                    contentStyle={tooltipStyle(chart)}
                    formatter={(value) => [`${value} h`, "Horas"]}
                  />
                  <Line
                    type="monotone"
                    dataKey="horas"
                    stroke="#818cf8"
                    strokeWidth={2.5}
                    dot={{ fill: "#6366f1", r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </section>

        <section className="shell-panel">
          <h2>Tempo por disciplina</h2>
          <p className="shell-panel-sub">Comparativo de dedicação</p>
          <div className="shell-chart-wrap">
            {carregando ? (
              <p className="shell-empty">Carregando…</p>
            ) : tempoDisciplinas.length === 0 ? (
              <p className="shell-empty">Nenhuma hora registrada por disciplina.</p>
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart
                  data={tempoDisciplinas}
                  layout="vertical"
                  margin={{ top: 4, right: 16, left: 4, bottom: 4 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke={chart.grid} horizontal={false} />
                  <XAxis
                    type="number"
                    tick={{ fill: chart.tick, fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                    domain={[0, "auto"]}
                  />
                  <YAxis
                    type="category"
                    dataKey="disciplina"
                    width={88}
                    tick={{ fill: chart.tick, fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip
                    contentStyle={tooltipStyle(chart)}
                    formatter={(value) => [`${value} h`, "Horas"]}
                  />
                  <Bar dataKey="horas" fill="#6366f1" radius={[0, 6, 6, 0]} maxBarSize={22} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </section>
      </div>
    </>
  );
}
