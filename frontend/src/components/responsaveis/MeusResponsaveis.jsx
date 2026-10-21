import { useCallback, useEffect, useState } from "react";
import { Plus, Users } from "lucide-react";
import { extrairMensagemErro } from "../../services/api";
import {
  cancelarConvite,
  listarMeusResponsaveis,
  reenviarConvite,
  removerVinculo,
} from "../../services/responsavelService";
import CadastrarResponsavelModal from "./CadastrarResponsavelModal";
import ResponsavelCard from "./ResponsavelCard";

export default function MeusResponsaveis({ onMensagem }) {
  const [itens, setItens] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [modalAberto, setModalAberto] = useState(false);
  const [ocupado, setOcupado] = useState(false);

  const carregar = useCallback(async () => {
    setErro("");
    try {
      const { data } = await listarMeusResponsaveis();
      setItens(data.itens || []);
    } catch (e) {
      setErro(extrairMensagemErro(e));
    } finally {
      setCarregando(false);
    }
  }, []);

  useEffect(() => {
    carregar();
  }, [carregar]);

  async function handleRemover(item) {
    if (
      !window.confirm(
        "Deseja remover o acesso deste responsável ao seu acompanhamento de estudos?"
      )
    ) {
      return;
    }
    setOcupado(true);
    try {
      await removerVinculo(item.id);
      onMensagem?.("Responsável removido com sucesso.");
      await carregar();
    } catch (e) {
      onMensagem?.(extrairMensagemErro(e), true);
    } finally {
      setOcupado(false);
    }
  }

  async function handleReenviar(item) {
    setOcupado(true);
    try {
      const { data } = await reenviarConvite(item.id);
      onMensagem?.(data.mensagem || "Convite reenviado.");
      if (data.link_desenvolvimento) {
        console.info("[StudyHub] Link do convite:", data.link_desenvolvimento);
      }
      await carregar();
    } catch (e) {
      onMensagem?.(extrairMensagemErro(e), true);
    } finally {
      setOcupado(false);
    }
  }

  async function handleCancelar(item) {
    if (!window.confirm("Cancelar este convite pendente?")) return;
    setOcupado(true);
    try {
      await cancelarConvite(item.id);
      onMensagem?.("Convite cancelado.");
      await carregar();
    } catch (e) {
      onMensagem?.(extrairMensagemErro(e), true);
    } finally {
      setOcupado(false);
    }
  }

  function handleSucessoConvite(data) {
    onMensagem?.(data.mensagem || "Convite enviado.");
    if (data.link_desenvolvimento) {
      console.info("[StudyHub] Link do convite:", data.link_desenvolvimento);
    }
    carregar();
  }

  return (
    <section className="shell-perfil-card resp-secao">
      <div className="resp-secao-head">
        <div>
          <h2>
            <Users size={18} aria-hidden /> Meus Responsáveis
          </h2>
          <p>Cadastre pessoas de confiança para acompanhar seu progresso nos estudos.</p>
        </div>
        <button
          type="button"
          className="shell-btn-primary"
          onClick={() => setModalAberto(true)}
        >
          <Plus size={16} /> Cadastrar Responsável
        </button>
      </div>

      {carregando ? <p className="resp-muted">Carregando…</p> : null}
      {erro ? <p className="shell-form-erro">{erro}</p> : null}

      {!carregando && itens.length === 0 ? (
        <p className="resp-muted">Nenhum responsável cadastrado ainda.</p>
      ) : null}

      <div className="resp-lista">
        {itens.map((item) => (
          <ResponsavelCard
            key={`${item.tipo}-${item.id}`}
            item={item}
            ocupado={ocupado}
            onRemover={handleRemover}
            onReenviar={handleReenviar}
            onCancelar={handleCancelar}
          />
        ))}
      </div>

      <CadastrarResponsavelModal
        aberto={modalAberto}
        onFechar={() => setModalAberto(false)}
        onSucesso={handleSucessoConvite}
      />
    </section>
  );
}
