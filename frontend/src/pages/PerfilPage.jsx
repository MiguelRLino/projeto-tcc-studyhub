import { useCallback, useEffect, useState } from "react";
import {
  Award,
  Bell,
  ChevronDown,
  Flame,
  Lock,
  Palette,
  Pencil,
  Target,
  Trash2,
  TrendingUp,
  Trophy,
  User,
} from "lucide-react";
import TelegramConfiguracao from "../components/telegram/TelegramConfiguracao";
import { extrairMensagemErro } from "../services/api";
import { atualizarAlunoLocal, limparSessao, obterAluno } from "../services/authService";
import {
  alterarSenha,
  atualizarPerfil,
  excluirConta,
  obterPerfil,
} from "../services/perfilService";
import { obterPreferencias, salvarPreferencias, TEMA_CLARO, TEMA_ESCURO } from "../utils/tema";

function iconeConquista(cor) {
  if (cor === "azul") return <Target size={18} color="#93c5fd" />;
  if (cor === "verde") return <Award size={18} color="#6ee7b7" />;
  return <Flame size={18} color="#c4b5fd" />;
}

export default function PerfilPage() {
  const [perfil, setPerfil] = useState(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [sucesso, setSucesso] = useState("");
  const [modalEditar, setModalEditar] = useState(false);
  const [modalSenha, setModalSenha] = useState(false);
  const [nomeForm, setNomeForm] = useState("");
  const [senhaAtual, setSenhaAtual] = useState("");
  const [senhaNova, setSenhaNova] = useState("");
  const [salvando, setSalvando] = useState(false);
  const [prefs, setPrefs] = useState(() => obterPreferencias());

  const carregar = useCallback(async () => {
    setErro("");
    try {
      const { data } = await obterPerfil();
      setPerfil(data);
      setNomeForm(data.nome ?? "");
      atualizarAlunoLocal({
        id_aluno: data.id_aluno,
        nome: data.nome,
        email: data.email,
      });
    } catch (e) {
      const aluno = obterAluno();
      if (aluno) {
        setPerfil({
          nome: aluno.nome,
          email: aluno.email,
          papel: "Estudante",
          membro_desde_label: "—",
          conquistas_total: 0,
          conquistas: [],
          estatisticas: {
            produtividade_pct: 0,
            metas_atingidas: 0,
            metas_total: 1,
            ranking: 1,
          },
        });
      }
      setErro(extrairMensagemErro(e));
    } finally {
      setCarregando(false);
    }
  }, []);

  useEffect(() => {
    carregar();
  }, [carregar]);

  function atualizarPrefs(patch) {
    const next = salvarPreferencias(patch);
    setPrefs(next);
  }

  function abrirEditar() {
    setNomeForm(perfil?.nome ?? "");
    setModalEditar(true);
  }

  async function salvarNome(e) {
    e.preventDefault();
    setSalvando(true);
    setErro("");
    setSucesso("");
    try {
      const { data } = await atualizarPerfil({ nome: nomeForm.trim() });
      setPerfil(data);
      atualizarAlunoLocal({
        id_aluno: data.id_aluno,
        nome: data.nome,
        email: data.email,
      });
      setModalEditar(false);
      setSucesso("Perfil atualizado.");
    } catch (err) {
      setErro(extrairMensagemErro(err));
    } finally {
      setSalvando(false);
    }
  }

  async function salvarSenha(e) {
    e.preventDefault();
    setSalvando(true);
    setErro("");
    setSucesso("");
    try {
      await alterarSenha({
        senha_atual: senhaAtual,
        senha_nova: senhaNova,
      });
      setModalSenha(false);
      setSenhaAtual("");
      setSenhaNova("");
      setSucesso("Senha alterada com sucesso.");
    } catch (err) {
      setErro(extrairMensagemErro(err));
    } finally {
      setSalvando(false);
    }
  }

  async function handleExcluirConta() {
    const ok = window.confirm(
      "Excluir sua conta permanentemente?\n\nTodos os seus dados serão removidos. Esta ação não pode ser desfeita.",
    );
    if (!ok) return;
    setErro("");
    try {
      await excluirConta();
      limparSessao();
      window.location.href = "/cadastro";
    } catch (err) {
      setErro(extrairMensagemErro(err));
    }
  }

  const stats = perfil?.estatisticas;
  const prodPct = stats?.produtividade_pct ?? 0;
  const prodPositivo = prodPct >= 0;

  return (
    <>
      <header className="shell-page-head">
        <h1>Perfil</h1>
        <p>Gerencie suas informações e preferências</p>
      </header>

      {erro ? (
        <div className="shell-alert" role="alert">
          {erro}
        </div>
      ) : null}
      {sucesso ? (
        <div className="shell-perfil-sucesso" role="status">
          {sucesso}
        </div>
      ) : null}

      <div className="shell-perfil-grid">
        <div className="shell-perfil-col">
          <section className="shell-perfil-card shell-perfil-user">
            <button
              type="button"
              className="shell-perfil-editar"
              onClick={abrirEditar}
              disabled={carregando}
            >
              <Pencil size={14} aria-hidden />
              Editar
            </button>

            <div className="shell-perfil-user-top">
              <div className="shell-perfil-avatar" aria-hidden>
                <User size={36} strokeWidth={1.75} />
              </div>
              <div>
                <h2>{carregando ? "…" : perfil?.nome || "Estudante"}</h2>
                <span className="shell-perfil-papel">{perfil?.papel || "Estudante"}</span>
              </div>
            </div>

            <div className="shell-perfil-detalhes">
              <div>
                <span className="label">Email</span>
                <p>{carregando ? "…" : perfil?.email}</p>
              </div>
              <div>
                <span className="label">Membro desde</span>
                <p>{carregando ? "…" : perfil?.membro_desde_label || "—"}</p>
              </div>
            </div>
          </section>

          <section className="shell-perfil-card">
            <h3>Configurações</h3>

            <div className="shell-perfil-setting">
              <div className="shell-perfil-setting-icon" aria-hidden>
                <Bell size={18} color="#a5b4fc" />
              </div>
              <div className="shell-perfil-setting-text">
                <strong>Notificações</strong>
                <span>Receber lembretes e alertas</span>
              </div>
              <button
                type="button"
                className={`shell-perfil-toggle${prefs.notificacoes ? " is-on" : ""}`}
                role="switch"
                aria-checked={prefs.notificacoes}
                onClick={() => atualizarPrefs({ notificacoes: !prefs.notificacoes })}
              >
                <span className="shell-perfil-toggle-knob" />
              </button>
            </div>

            <div className="shell-perfil-setting">
              <div className="shell-perfil-setting-icon" aria-hidden>
                <Palette size={18} color="#c4b5fd" />
              </div>
              <div className="shell-perfil-setting-text">
                <strong>Tema</strong>
                <span>Personalizar aparência</span>
              </div>
              <div className="shell-perfil-select-wrap">
                <select
                  value={prefs.tema}
                  onChange={(e) => atualizarPrefs({ tema: e.target.value })}
                  aria-label="Tema da interface"
                >
                  <option value={TEMA_ESCURO}>Escuro</option>
                  <option value={TEMA_CLARO}>Claro</option>
                </select>
                <ChevronDown size={16} className="shell-perfil-select-icon" aria-hidden />
              </div>
            </div>

            <button
              type="button"
              className="shell-perfil-alterar-senha"
              onClick={() => setModalSenha(true)}
            >
              <Lock size={16} aria-hidden />
              Alterar Senha
            </button>
          </section>

          <TelegramConfiguracao />
        </div>

        <div className="shell-perfil-col">
          <section className="shell-perfil-card shell-perfil-conquistas-card">
            <div className="shell-perfil-conquistas-head">
              <div className="shell-perfil-medal" aria-hidden>
                <Award size={28} color="#fb923c" />
              </div>
              <div>
                <h3>
                  {carregando ? "…" : perfil?.conquistas_total ?? 0} Conquistas
                </h3>
                <p>Continue estudando!</p>
              </div>
            </div>

            <ul className="shell-perfil-conquistas-list">
              {(perfil?.conquistas ?? []).map((c) => (
                <li
                  key={c.id}
                  className={c.desbloqueada ? "" : "is-locked"}
                >
                  <div className={`shell-perfil-conq-icon cor-${c.cor}`}>
                    {iconeConquista(c.cor)}
                  </div>
                  <div>
                    <strong>{c.titulo}</strong>
                    <span>{c.descricao}</span>
                  </div>
                </li>
              ))}
              {!carregando && !perfil?.conquistas?.length ? (
                <li className="shell-perfil-conq-empty">
                  Estude para desbloquear conquistas.
                </li>
              ) : null}
            </ul>
          </section>

          <section className="shell-perfil-card">
            <h3>Estatísticas Rápidas</h3>
            <ul className="shell-perfil-stats-list">
              <li>
                <div className="shell-perfil-stat-icon green">
                  <TrendingUp size={18} />
                </div>
                <span>Produtividade</span>
                <strong className={prodPositivo ? "up" : "down"}>
                  {prodPositivo ? "+" : ""}
                  {carregando ? "…" : prodPct}%
                </strong>
              </li>
              <li>
                <div className="shell-perfil-stat-icon purple">
                  <Target size={18} />
                </div>
                <span>Metas atingidas</span>
                <strong>
                  {carregando
                    ? "…"
                    : `${stats?.metas_atingidas ?? 0}/${stats?.metas_total ?? 0}`}
                </strong>
              </li>
              <li>
                <div className="shell-perfil-stat-icon orange">
                  <Trophy size={18} />
                </div>
                <span>Ranking</span>
                <strong>#{carregando ? "…" : stats?.ranking ?? "—"}</strong>
              </li>
            </ul>
          </section>

          <section className="shell-perfil-card shell-perfil-danger">
            <h3>Zona de Perigo</h3>
            <p>
              Ao excluir sua conta, todos os dados (disciplinas, tarefas e sessões) serão
              removidos permanentemente.
            </p>
            <button type="button" className="shell-perfil-btn-excluir" onClick={handleExcluirConta}>
              <Trash2 size={16} aria-hidden />
              Excluir conta
            </button>
          </section>
        </div>
      </div>

      {modalEditar ? (
        <div
          className="shell-modal-overlay"
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-perfil-titulo"
          onClick={(ev) => {
            if (ev.target === ev.currentTarget && !salvando) setModalEditar(false);
          }}
        >
          <div className="shell-modal">
            <h2 id="modal-perfil-titulo">Editar perfil</h2>
            <form onSubmit={salvarNome}>
              <div className="shell-field">
                <label htmlFor="perfil-nome">Nome</label>
                <input
                  id="perfil-nome"
                  value={nomeForm}
                  onChange={(e) => setNomeForm(e.target.value)}
                  required
                  maxLength={100}
                  autoFocus
                />
              </div>
              <div className="shell-modal-actions">
                <button
                  type="button"
                  className="shell-btn-ghost"
                  onClick={() => setModalEditar(false)}
                  disabled={salvando}
                >
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

      {modalSenha ? (
        <div
          className="shell-modal-overlay"
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-senha-titulo"
          onClick={(ev) => {
            if (ev.target === ev.currentTarget && !salvando) setModalSenha(false);
          }}
        >
          <div className="shell-modal">
            <h2 id="modal-senha-titulo">Alterar senha</h2>
            <form onSubmit={salvarSenha}>
              <div className="shell-field">
                <label htmlFor="senha-atual">Senha atual</label>
                <input
                  id="senha-atual"
                  type="password"
                  value={senhaAtual}
                  onChange={(e) => setSenhaAtual(e.target.value)}
                  required
                  autoComplete="current-password"
                />
              </div>
              <div className="shell-field">
                <label htmlFor="senha-nova">Nova senha</label>
                <input
                  id="senha-nova"
                  type="password"
                  value={senhaNova}
                  onChange={(e) => setSenhaNova(e.target.value)}
                  required
                  minLength={8}
                  autoComplete="new-password"
                />
              </div>
              <div className="shell-modal-actions">
                <button
                  type="button"
                  className="shell-btn-ghost"
                  onClick={() => setModalSenha(false)}
                  disabled={salvando}
                >
                  Cancelar
                </button>
                <button type="submit" className="shell-btn-primary" disabled={salvando}>
                  {salvando ? "Salvando…" : "Alterar"}
                </button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </>
  );
}
