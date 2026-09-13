import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate, useOutletContext, useParams } from "react-router-dom";
import { ChevronRight, FilePlus, Save } from "lucide-react";
import EditorTiptap from "../components/cadernos/EditorTiptap";
import ToolbarEditor from "../components/cadernos/ToolbarEditor";
import PainelPagina from "../components/cadernos/PainelPagina";
import EstadoSalvamento from "../components/cadernos/EstadoSalvamento";
import ModalMoverPagina from "../components/cadernos/ModalMoverPagina";
import { useAutoSave } from "../hooks/useAutoSave";
import { extrairMensagemErro } from "../services/api";
import { listarCadernos } from "../services/cadernoService";
import {
  listarPaginas,
  atualizarPagina,
  criarPagina,
  duplicarPagina,
  excluirPagina,
  favoritarPagina,
  moverPagina,
  obterPagina,
  registrarExportacaoPdf,
  uploadImagemPagina,
} from "../services/paginaCadernoService";
import { calcularMetricas, CONTEUDO_VAZIO, normalizarConteudo } from "../utils/cadernoMetricas";
import { exportarPdfCaderno } from "../utils/exportarPdfCaderno";
import { CadernoVazio } from "./CadernosLayout";

export default function EditorPage() {
  const { cadernoId, paginaId } = useParams();
  const navigate = useNavigate();
  const { recarregar } = useOutletContext();
  const editorRef = useRef(null);
  const paperRef = useRef(null);
  const inputImagemRef = useRef(null);
  const tituloRef = useRef("");
  const conteudoRef = useRef(CONTEUDO_VAZIO);

  const [pagina, setPagina] = useState(null);
  const [titulo, setTitulo] = useState("");
  const [conteudo, setConteudo] = useState(CONTEUDO_VAZIO);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [editorInst, setEditorInst] = useState(null);
  const [zoom, setZoom] = useState(100);
  const [telaCheia, setTelaCheia] = useState(false);
  const [modalMover, setModalMover] = useState(false);
  const [cadernos, setCadernos] = useState([]);
  const [acaoCarregando, setAcaoCarregando] = useState(false);

  const metricas = useMemo(() => calcularMetricas(conteudo), [conteudo]);

  const salvarFn = useCallback(
    async (payload) => {
      await atualizarPagina(paginaId, payload);
      recarregar?.();
    },
    [paginaId, recarregar],
  );

  const { estado: estadoSalvamento, disparar, resetUltimoSalvo } = useAutoSave(
    salvarFn,
    2000,
  );

  const carregarPagina = useCallback(async () => {
    setCarregando(true);
    setErro("");
    try {
      const { data } = await obterPagina(paginaId);
      setPagina(data);
      setTitulo(data.titulo || "");
      const conteudoNorm = normalizarConteudo(data.conteudo);
      setConteudo(conteudoNorm);
      tituloRef.current = data.titulo || "";
      conteudoRef.current = conteudoNorm;
      resetUltimoSalvo();
    } catch (e) {
      const msg = extrairMensagemErro(e);
      if (e.response?.status === 404) setErro("Página não encontrada.");
      else if (e.response?.status === 403) setErro("Você não possui permissão.");
      else setErro(msg || "Erro ao carregar anotações.");
    } finally {
      setCarregando(false);
    }
  }, [paginaId, resetUltimoSalvo]);

  useEffect(() => {
    carregarPagina();
  }, [carregarPagina]);

  useEffect(() => {
    listarCadernos()
      .then(({ data }) => setCadernos(Array.isArray(data) ? data : []))
      .catch(() => setCadernos([]));
  }, []);

  function agendarSalvar(novoTitulo, novoConteudo) {
    tituloRef.current = novoTitulo;
    conteudoRef.current = novoConteudo;
    disparar({ titulo: novoTitulo, conteudo: novoConteudo });
  }

  function handleTituloChange(e) {
    const v = e.target.value;
    setTitulo(v);
    agendarSalvar(v, conteudoRef.current);
  }

  function handleConteudoChange(json) {
    setConteudo(json);
    conteudoRef.current = json;
    agendarSalvar(tituloRef.current, json);
  }

  async function salvarAgora() {
    await disparar(
      { titulo: tituloRef.current, conteudo: conteudoRef.current },
      { imediato: true },
    );
  }

  async function handleInserirImagem() {
    inputImagemRef.current?.click();
  }

  async function handleArquivoImagem(e) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    try {
      const { data } = await uploadImagemPagina(paginaId, file);
      editorRef.current?.insertImage(data.url);
    } catch (err) {
      window.alert(extrairMensagemErro(err));
    }
  }

  useEffect(() => {
    if (!editorInst) return;
    const onPaste = async (event) => {
      const items = event.clipboardData?.items;
      if (!items) return;
      for (const item of items) {
        if (item.type.startsWith("image/")) {
          event.preventDefault();
          const file = item.getAsFile();
          if (!file) return;
          try {
            const { data } = await uploadImagemPagina(paginaId, file);
            editorRef.current?.insertImage(data.url);
          } catch (err) {
            window.alert(extrairMensagemErro(err));
          }
          break;
        }
      }
    };
    const el = editorInst.view.dom;
    el.addEventListener("paste", onPaste);
    return () => el.removeEventListener("paste", onPaste);
  }, [editorInst, paginaId]);

  async function handleFavoritar() {
    setAcaoCarregando(true);
    try {
      const { data } = await favoritarPagina(paginaId, !pagina.favorita);
      setPagina(data);
      recarregar?.();
    } catch (e) {
      window.alert(extrairMensagemErro(e));
    } finally {
      setAcaoCarregando(false);
    }
  }

  async function handleDuplicar() {
    setAcaoCarregando(true);
    try {
      const { data } = await duplicarPagina(paginaId);
      recarregar?.();
      navigate(`/cadernos/${data.id_caderno}/paginas/${data.id_pagina}`);
    } catch (e) {
      window.alert(extrairMensagemErro(e));
    } finally {
      setAcaoCarregando(false);
    }
  }

  async function handleMover(destinoId) {
    const { data } = await moverPagina(paginaId, destinoId);
    recarregar?.();
    navigate(`/cadernos/${data.id_caderno}/paginas/${data.id_pagina}`);
  }

  async function handleExcluir() {
    if (!window.confirm(`Excluir a página "${pagina.titulo}"?`)) return;
    setAcaoCarregando(true);
    try {
      await excluirPagina(paginaId);
      recarregar?.();
      navigate(`/cadernos/${cadernoId}`);
    } catch (e) {
      window.alert(extrairMensagemErro(e));
    } finally {
      setAcaoCarregando(false);
    }
  }

  async function handleExportarPdf() {
    try {
      await exportarPdfCaderno(paperRef.current, titulo);
      await registrarExportacaoPdf(paginaId).catch(() => {});
    } catch {
      window.alert("Não foi possível exportar o PDF.");
    }
  }

  function handleImprimir() {
    window.print();
  }

  function handleIaPlaceholder() {
    navigate("/assistente");
  }

  async function novaPaginaRapida() {
    const t = window.prompt("Título da nova página:", "Sem título");
    if (t === null) return;
    try {
      const { data } = await criarPagina(cadernoId, {
        titulo: t.trim() || "Sem título",
      });
      recarregar?.();
      navigate(`/cadernos/${cadernoId}/paginas/${data.id_pagina}`);
    } catch (e) {
      window.alert(extrairMensagemErro(e));
    }
  }

  if (carregando) {
    return <div className="caderno-loading">Carregando página…</div>;
  }

  if (erro) {
    return (
      <div className="caderno-welcome">
        <p className="caderno-erro">{erro}</p>
        <Link to="/cadernos">Voltar aos cadernos</Link>
      </div>
    );
  }

  if (!pagina) {
    return (
      <div className="caderno-welcome">
        <p className="caderno-erro">Não foi possível carregar a página.</p>
        <Link to="/cadernos">Voltar aos cadernos</Link>
      </div>
    );
  }

  return (
    <div className={`caderno-editor-shell${telaCheia ? " is-fullscreen" : ""}`}>
      <header className="caderno-editor-header">
        <nav className="caderno-breadcrumb">
          <Link to="/cadernos">Cadernos</Link>
          <ChevronRight size={14} />
          <Link to={`/cadernos/${cadernoId}`}>{pagina.caderno_titulo}</Link>
          <ChevronRight size={14} />
          <span>{titulo || "Sem título"}</span>
        </nav>
        <div className="caderno-editor-header-actions">
          <EstadoSalvamento estado={estadoSalvamento} />
          <button type="button" className="caderno-btn ghost sm" onClick={salvarAgora}>
            <Save size={16} />
            Salvar agora
          </button>
          <button type="button" className="caderno-btn ghost sm" onClick={novaPaginaRapida}>
            <FilePlus size={16} />
            Nova página
          </button>
        </div>
      </header>

      <input
        className="caderno-titulo-input"
        value={titulo}
        onChange={handleTituloChange}
        placeholder="Título da página"
        maxLength={200}
      />

      <ToolbarEditor
        editor={editorInst}
        onInserirImagem={handleInserirImagem}
        telaCheia={telaCheia}
        onToggleTelaCheia={() => setTelaCheia((v) => !v)}
        zoom={zoom}
        onZoomChange={setZoom}
      />

      <div className="caderno-editor-body">
        <div className="caderno-editor-center">
          <EditorTiptap
            key={paginaId}
            ref={editorRef}
            paperRef={paperRef}
            conteudo={conteudo}
            onChange={handleConteudoChange}
            onEditorReady={setEditorInst}
            zoom={zoom}
          />
        </div>

        {!telaCheia && (
          <PainelPagina
            pagina={{ ...pagina, ...metricas, tempo_leitura_min: metricas.leituraMin }}
            metricas={metricas}
            onFavoritar={handleFavoritar}
            onDuplicar={handleDuplicar}
            onMover={() => setModalMover(true)}
            onExportarPdf={handleExportarPdf}
            onImprimir={handleImprimir}
            onExcluir={handleExcluir}
            onIaPlaceholder={handleIaPlaceholder}
            acaoCarregando={acaoCarregando}
          />
        )}
      </div>

      <input
        ref={inputImagemRef}
        type="file"
        accept="image/jpeg,image/png,image/gif,image/webp"
        hidden
        onChange={handleArquivoImagem}
      />

      <ModalMoverPagina
        aberto={modalMover}
        pagina={pagina}
        cadernos={cadernos}
        onFechar={() => setModalMover(false)}
        onMover={handleMover}
      />
    </div>
  );
}

export function CadernoHubPage() {
  const { cadernoId } = useParams();
  const navigate = useNavigate();
  const [temPaginas, setTemPaginas] = useState(null);

  useEffect(() => {
    listarPaginas(cadernoId)
      .then(({ data }) => {
        const lista = Array.isArray(data) ? data : [];
        setTemPaginas(lista.length > 0);
        if (lista.length > 0) {
          navigate(`/cadernos/${cadernoId}/paginas/${lista[0].id_pagina}`, {
            replace: true,
          });
        }
      })
      .catch(() => setTemPaginas(false));
  }, [cadernoId, navigate]);

  if (temPaginas === false) return <CadernoVazio cadernoId={cadernoId} />;
  return <div className="caderno-loading">Carregando caderno…</div>;
}
