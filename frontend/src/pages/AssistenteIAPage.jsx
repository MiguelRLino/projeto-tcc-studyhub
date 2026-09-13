import { Sparkles } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { extrairMensagemErro } from "../services/api";
import {
  enviarPergunta,
  excluirConversa,
  listarHistorico,
} from "../services/assistenteService";
import ChatInput from "../components/assistente/ChatInput";
import ChatMensagem from "../components/assistente/ChatMensagem";
import HistoricoConversas from "../components/assistente/HistoricoConversas";
import SugestoesRapidas from "../components/assistente/SugestoesRapidas";
import "../styles/assistente.css";

export default function AssistenteIAPage() {
  const [mensagens, setMensagens] = useState([]);
  const [entrada, setEntrada] = useState("");
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState("");
  const [historico, setHistorico] = useState([]);
  const [historicoCarregando, setHistoricoCarregando] = useState(true);
  const [conversaSelecionadaId, setConversaSelecionadaId] = useState(null);
  const chatRef = useRef(null);

  const carregarHistorico = useCallback(async () => {
    setHistoricoCarregando(true);
    try {
      const { data } = await listarHistorico();
      setHistorico(Array.isArray(data) ? data : []);
    } catch {
      setHistorico([]);
    } finally {
      setHistoricoCarregando(false);
    }
  }, []);

  useEffect(() => {
    carregarHistorico();
  }, [carregarHistorico]);

  useEffect(() => {
    chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: "smooth" });
  }, [mensagens, carregando]);

  async function handleEnviar(textoOverride) {
    const pergunta = (textoOverride ?? entrada).trim();
    if (!pergunta || carregando) return;

    setErro("");
    setEntrada("");
    setConversaSelecionadaId(null);
    setMensagens((prev) => [...prev, { tipo: "aluno", texto: pergunta }]);
    setCarregando(true);

    try {
      const { data } = await enviarPergunta(pergunta);
      setMensagens((prev) => [...prev, { tipo: "ia", texto: data.resposta }]);
      await carregarHistorico();
    } catch (e) {
      const msg = extrairMensagemErro(e);
      setErro(msg);
      setMensagens((prev) => prev.slice(0, -1));
      if (!textoOverride) setEntrada(pergunta);
    } finally {
      setCarregando(false);
    }
  }

  function handleSelecionarConversa(item) {
    setConversaSelecionadaId(item.id_conversa);
    setErro("");
    setMensagens([
      { tipo: "aluno", texto: item.pergunta },
      { tipo: "ia", texto: item.resposta },
    ]);
  }

  function handleNovaConversa() {
    setConversaSelecionadaId(null);
    setMensagens([]);
    setEntrada("");
    setErro("");
  }

  async function handleExcluirConversa(id) {
    if (!window.confirm("Excluir esta conversa do histórico?")) return;
    try {
      await excluirConversa(id);
      if (conversaSelecionadaId === id) handleNovaConversa();
      await carregarHistorico();
    } catch (e) {
      setErro(extrairMensagemErro(e));
    }
  }

  return (
    <div className="ia-page">
      <header className="shell-page-head ia-page-head">
        <div>
          <h1>
            <Sparkles size={24} className="ia-head-icon" />
            Assistente IA
          </h1>
          <p>Tire dúvidas e receba ajuda para organizar seus estudos.</p>
        </div>
        <button type="button" className="ia-btn-nova" onClick={handleNovaConversa}>
          Nova conversa
        </button>
      </header>

      <div className="ia-layout">
        <aside className="ia-historico-panel">
          <h3>Histórico</h3>
          <HistoricoConversas
            itens={historico}
            selecionadaId={conversaSelecionadaId}
            onSelecionar={handleSelecionarConversa}
            onExcluir={handleExcluirConversa}
            carregando={historicoCarregando}
          />
        </aside>

        <section className="ia-chat-panel">
          <SugestoesRapidas
            onSelecionar={(texto) => setEntrada(texto)}
            desabilitado={carregando}
          />

          <div className="ia-chat-area" ref={chatRef}>
            {mensagens.length === 0 && !carregando && (
              <div className="ia-chat-vazio">
                <Sparkles size={32} />
                <p>Como posso ajudar nos seus estudos hoje?</p>
              </div>
            )}
            {mensagens.map((msg, i) => (
              <ChatMensagem key={`${msg.tipo}-${i}`} tipo={msg.tipo} texto={msg.texto} />
            ))}
            {carregando && (
              <div className="ia-pensando">
                <span className="ia-pensando-dot" />
                <span className="ia-pensando-dot" />
                <span className="ia-pensando-dot" />
                Pensando...
              </div>
            )}
          </div>

          {erro && (
            <div className="shell-alert ia-erro" role="alert">
              {erro}
            </div>
          )}

          <ChatInput
            valor={entrada}
            onChange={setEntrada}
            onEnviar={() => handleEnviar()}
            carregando={carregando}
          />
        </section>
      </div>
    </div>
  );
}
