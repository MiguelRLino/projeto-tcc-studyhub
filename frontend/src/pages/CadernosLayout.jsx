import { useCallback, useRef, useState } from "react";
import {
  Link,
  Outlet,
  useNavigate,
  useOutletContext,
} from "react-router-dom";
import { BookOpen, FilePlus } from "lucide-react";
import { extrairMensagemErro } from "../services/api";
import { atualizarCaderno, criarCaderno } from "../services/cadernoService";
import { criarPagina } from "../services/paginaCadernoService";
import { listarDisciplinas } from "../services/disciplinasService";
import CadernosSidebar from "../components/cadernos/CadernosSidebar";
import ModalCaderno from "../components/cadernos/ModalCaderno";
import "../styles/cadernos.css";

export default function CadernosLayout() {
  const navigate = useNavigate();
  const [modalCaderno, setModalCaderno] = useState(null);
  const [disciplinas, setDisciplinas] = useState([]);
  const [recarregarToken, setRecarregarToken] = useState(0);
  const disciplinasCarregadas = useRef(false);

  const recarregar = useCallback(() => {
    setRecarregarToken((t) => t + 1);
  }, []);

  async function garantirDisciplinas() {
    if (disciplinasCarregadas.current) return;
    try {
      const { data } = await listarDisciplinas();
      setDisciplinas(Array.isArray(data) ? data : data?.results ?? []);
      disciplinasCarregadas.current = true;
    } catch {
      setDisciplinas([]);
    }
  }

  async function abrirNovoCaderno() {
    await garantirDisciplinas();
    setModalCaderno({ modo: "criar" });
  }

  async function abrirEditarCaderno(caderno) {
    await garantirDisciplinas();
    setModalCaderno({ modo: "editar", caderno });
  }

  async function salvarCaderno(payload) {
    if (modalCaderno?.modo === "editar") {
      await atualizarCaderno(modalCaderno.caderno.id_caderno, payload);
    } else {
      const { data } = await criarCaderno(payload);
      recarregar();
      navigate(`/cadernos/${data.id_caderno}`);
    }
    recarregar();
  }

  async function novaPagina(caderno) {
    const titulo = window.prompt("Título da nova página:", "Sem título");
    if (titulo === null) return;
    try {
      const { data } = await criarPagina(caderno.id_caderno, {
        titulo: titulo.trim() || "Sem título",
      });
      recarregar();
      navigate(`/cadernos/${caderno.id_caderno}/paginas/${data.id_pagina}`);
    } catch (e) {
      window.alert(extrairMensagemErro(e));
    }
  }

  return (
    <div className="caderno-layout">
      <CadernosSidebar
        onNovoCaderno={abrirNovoCaderno}
        onEditarCaderno={abrirEditarCaderno}
        onNovaPagina={novaPagina}
        recarregarToken={recarregarToken}
      />
      <div className="caderno-main">
        <Outlet context={{ recarregar }} />
      </div>

      <ModalCaderno
        aberto={Boolean(modalCaderno)}
        modo={modalCaderno?.modo}
        caderno={modalCaderno?.caderno}
        disciplinas={disciplinas}
        onFechar={() => setModalCaderno(null)}
        onSalvar={salvarCaderno}
      />
    </div>
  );
}

export function CadernosWelcome() {
  return (
    <div className="caderno-welcome">
      <div className="caderno-welcome-icon">
        <BookOpen size={40} />
      </div>
      <h1>Caderno Digital</h1>
      <p>
        Organize suas anotações em cadernos e páginas. Crie um caderno na barra
        lateral ou selecione um existente para começar.
      </p>
    </div>
  );
}

export function CadernoVazio({ cadernoId }) {
  const { recarregar } = useOutletContext();
  const navigate = useNavigate();

  async function criar() {
    const titulo = window.prompt("Título da primeira página:", "Sem título");
    if (titulo === null) return;
    try {
      const { data } = await criarPagina(cadernoId, {
        titulo: titulo.trim() || "Sem título",
      });
      recarregar?.();
      navigate(`/cadernos/${cadernoId}/paginas/${data.id_pagina}`);
    } catch (e) {
      window.alert(extrairMensagemErro(e));
    }
  }

  return (
    <div className="caderno-welcome">
      <h2>Este caderno ainda não tem páginas</h2>
      <p>Crie a primeira página para começar a escrever.</p>
      <button type="button" className="caderno-btn primary" onClick={criar}>
        <FilePlus size={16} />
        Nova página
      </button>
      <p className="caderno-muted">
        <Link to="/cadernos">Voltar</Link>
      </p>
    </div>
  );
}
