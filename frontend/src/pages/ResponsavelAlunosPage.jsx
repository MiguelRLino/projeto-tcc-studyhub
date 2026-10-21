import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Users } from "lucide-react";
import { extrairMensagemErro } from "../services/api";
import { listarMeusAlunos } from "../services/responsavelService";

const LABEL_PARENTESCO = {
  PAI: "Pai",
  MAE: "Mãe",
  OUTRO: "Outro responsável",
};

export default function ResponsavelAlunosPage() {
  const [alunos, setAlunos] = useState([]);
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    let ativo = true;
    async function carregar() {
      try {
        const { data } = await listarMeusAlunos();
        if (ativo) setAlunos(data.alunos || []);
      } catch (e) {
        if (ativo) setErro(extrairMensagemErro(e));
      } finally {
        if (ativo) setCarregando(false);
      }
    }
    carregar();
    return () => {
      ativo = false;
    };
  }, []);

  return (
    <div className="shell-page">
      <header className="shell-page-head">
        <div>
          <h1>
            <Users size={22} aria-hidden /> Meus Alunos
          </h1>
          <p>Selecione um aluno para acompanhar o desempenho.</p>
        </div>
      </header>

      {carregando ? <p>Carregando…</p> : null}
      {erro ? <p className="shell-form-erro">{erro}</p> : null}

      {!carregando && alunos.length === 0 ? (
        <section className="shell-perfil-card">
          <p>Você ainda não possui vínculos ativos com alunos.</p>
        </section>
      ) : null}

      <div className="resp-alunos-grid">
        {alunos.map((a) => (
          <article key={a.id_aluno} className="shell-perfil-card resp-aluno-card">
            <h3>{a.nome}</h3>
            <p>{a.email}</p>
            <p>Parentesco: {LABEL_PARENTESCO[a.parentesco] || a.parentesco}</p>
            <Link
              className="shell-btn-primary"
              to={`/responsavel/alunos/${a.id_aluno}`}
            >
              Visualizar desempenho
            </Link>
          </article>
        ))}
      </div>
    </div>
  );
}
