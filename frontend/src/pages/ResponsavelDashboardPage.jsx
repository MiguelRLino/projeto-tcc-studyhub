import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, BookOpen, CheckSquare, Clock } from "lucide-react";
import { extrairMensagemErro } from "../services/api";
import {
  listarMeusAlunos,
  obterDashboardAluno,
  obterDisciplinasAluno,
  obterRelatoriosAluno,
  obterSessoesAluno,
  obterTarefasAluno,
} from "../services/responsavelService";

export default function ResponsavelDashboardPage() {
  const { alunoId } = useParams();
  const [alunoSelecionado, setAlunoSelecionado] = useState(alunoId || null);
  const [alunos, setAlunos] = useState([]);
  const [dash, setDash] = useState(null);
  const [tarefas, setTarefas] = useState([]);
  const [disciplinas, setDisciplinas] = useState([]);
  const [sessoes, setSessoes] = useState({ realizadas: [], planejadas: [] });
  const [relatorios, setRelatorios] = useState(null);
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    listarMeusAlunos()
      .then(({ data }) => {
        const lista = data.alunos || [];
        setAlunos(lista);
        if (!alunoSelecionado && lista.length === 1) {
          setAlunoSelecionado(String(lista[0].id_aluno));
        }
      })
      .catch((e) => setErro(extrairMensagemErro(e)));
  }, [alunoSelecionado]);

  useEffect(() => {
    if (!alunoSelecionado) {
      setCarregando(false);
      return;
    }
    let ativo = true;
    setCarregando(true);
    setErro("");
    Promise.all([
      obterDashboardAluno(alunoSelecionado),
      obterTarefasAluno(alunoSelecionado),
      obterDisciplinasAluno(alunoSelecionado),
      obterSessoesAluno(alunoSelecionado),
      obterRelatoriosAluno(alunoSelecionado),
    ])
      .then(([d, t, disc, s, r]) => {
        if (!ativo) return;
        setDash(d.data);
        setTarefas(t.data.tarefas || []);
        setDisciplinas(disc.data.disciplinas || []);
        setSessoes(s.data || { realizadas: [], planejadas: [] });
        setRelatorios(r.data);
      })
      .catch((e) => {
        if (ativo) setErro(extrairMensagemErro(e));
      })
      .finally(() => {
        if (ativo) setCarregando(false);
      });
    return () => {
      ativo = false;
    };
  }, [alunoSelecionado]);

  if (!alunoSelecionado && !carregando) {
    return (
      <div className="shell-page">
        <header className="shell-page-head">
          <h1>Dashboard do responsável</h1>
          <p>Escolha um aluno para visualizar o acompanhamento.</p>
        </header>
        {erro ? <p className="shell-form-erro">{erro}</p> : null}
        <div className="resp-alunos-grid">
          {alunos.map((a) => (
            <button
              key={a.id_aluno}
              type="button"
              className="shell-perfil-card resp-aluno-card"
              onClick={() => setAlunoSelecionado(String(a.id_aluno))}
            >
              <h3>{a.nome}</h3>
              <p>Visualizar desempenho</p>
            </button>
          ))}
        </div>
        <p>
          <Link to="/responsavel/alunos">Ver lista completa</Link>
        </p>
      </div>
    );
  }

  const resumo = dash?.resumo || {};

  return (
    <div className="shell-page">
      <header className="shell-page-head">
        <div>
          {alunoId ? (
            <Link to="/responsavel/alunos" className="resp-back">
              <ArrowLeft size={16} /> Voltar
            </Link>
          ) : null}
          <h1>Acompanhamento — {dash?.aluno?.nome || "…"}</h1>
          <p>Visualização somente leitura do progresso acadêmico.</p>
        </div>
        {alunos.length > 1 ? (
          <label className="shell-field resp-select-aluno">
            <span>Aluno</span>
            <select
              value={alunoSelecionado || ""}
              onChange={(e) => setAlunoSelecionado(e.target.value)}
            >
              {alunos.map((a) => (
                <option key={a.id_aluno} value={a.id_aluno}>
                  {a.nome}
                </option>
              ))}
            </select>
          </label>
        ) : null}
      </header>

      {erro ? <p className="shell-form-erro">{erro}</p> : null}
      {carregando ? <p>Carregando dados…</p> : null}

      {!carregando && dash ? (
        <>
          <section className="resp-metricas">
            <article className="shell-perfil-card">
              <Clock size={18} />
              <strong>{resumo.horas_estudadas_semana ?? 0}h</strong>
              <span>Horas na semana</span>
            </article>
            <article className="shell-perfil-card">
              <BookOpen size={18} />
              <strong>{resumo.disciplinas_ativas ?? 0}</strong>
              <span>Disciplinas ativas</span>
            </article>
            <article className="shell-perfil-card">
              <CheckSquare size={18} />
              <strong>{resumo.tarefas_pendentes ?? 0}</strong>
              <span>Tarefas pendentes</span>
            </article>
            <article className="shell-perfil-card">
              <strong>{resumo.tarefas_atrasadas ?? 0}</strong>
              <span>Tarefas atrasadas</span>
            </article>
            <article className="shell-perfil-card">
              <strong>{resumo.sessoes_semana ?? 0}</strong>
              <span>Sessões na semana</span>
            </article>
          </section>

          <section className="shell-perfil-card">
            <h2>Evolução da semana</h2>
            <ul className="resp-grafico-lista">
              {(dash.grafico_horas_semana || []).map((d) => (
                <li key={d.dia}>
                  <span>{d.dia}</span>
                  <strong>{d.horas}h</strong>
                </li>
              ))}
            </ul>
          </section>

          <section className="shell-perfil-card">
            <h2>Tarefas</h2>
            {tarefas.length === 0 ? <p>Nenhuma tarefa.</p> : null}
            <ul className="resp-lista-simples">
              {tarefas.slice(0, 12).map((t) => (
                <li key={t.id_tarefa}>
                  <strong>{t.descricao || "Tarefa"}</strong>
                  <span>
                    {t.disciplina || "—"} · {t.data_entrega || "sem prazo"} ·{" "}
                    {t.atrasada
                      ? "Atrasada"
                      : t.concluida
                        ? "Concluída"
                        : t.status_tarefa || "Pendente"}
                  </span>
                </li>
              ))}
            </ul>
          </section>

          <section className="shell-perfil-card">
            <h2>Disciplinas</h2>
            <ul className="resp-lista-simples">
              {disciplinas.map((d) => (
                <li key={d.id_disciplina}>
                  <strong>{d.nome}</strong>
                  <span>
                    Dificuldade: {d.nivel_dificuldade ?? "—"} · {d.horas_estudadas}h
                    · {d.tarefas_pendentes} pendentes
                  </span>
                </li>
              ))}
            </ul>
          </section>

          <section className="shell-perfil-card">
            <h2>Sessões realizadas</h2>
            <ul className="resp-lista-simples">
              {(sessoes.realizadas || []).slice(0, 10).map((s) => (
                <li key={s.id_sessao_estudo}>
                  <strong>{s.disciplina || "Disciplina"}</strong>
                  <span>
                    {s.data_sessao || "—"} · {s.tempo_estudo}h
                  </span>
                </li>
              ))}
            </ul>
            {(sessoes.planejadas || []).length > 0 ? (
              <>
                <h3>Sessões planejadas</h3>
                <ul className="resp-lista-simples">
                  {sessoes.planejadas.slice(0, 8).map((s) => (
                    <li key={s.id_sessao_planejada}>
                      <strong>{s.disciplina || "Disciplina"}</strong>
                      <span>
                        {s.data_planejada || "—"} ·{" "}
                        {s.duracao_prevista_minutos || "—"} min
                      </span>
                    </li>
                  ))}
                </ul>
              </>
            ) : null}
          </section>

          {relatorios ? (
            <section className="shell-perfil-card">
              <h2>Relatórios</h2>
              <p>
                Total de horas: <strong>{relatorios.total_horas}h</strong> ·
                Melhor disciplina: <strong>{relatorios.melhor_disciplina}</strong> ·
                Tarefas concluídas: <strong>{relatorios.tarefas_concluidas}</strong>
              </p>
              <ul className="resp-lista-simples">
                {(relatorios.distribuicao_disciplinas || []).map((d) => (
                  <li key={d.disciplina}>
                    <strong>{d.disciplina}</strong>
                    <span>{d.horas}h</span>
                  </li>
                ))}
              </ul>
            </section>
          ) : null}
        </>
      ) : null}
    </div>
  );
}
