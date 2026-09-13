import { useCallback, useEffect, useState } from "react";
import { ExternalLink, MessageCircle } from "lucide-react";
import { extrairMensagemErro } from "../../services/api";
import {
  atualizarConfiguracaoTelegram,
  desconectarTelegram,
  gerarCodigoTelegram,
  obterConfiguracaoTelegram,
} from "../../services/telegramService";

export default function TelegramConfiguracao() {
  const [config, setConfig] = useState(null);
  const [carregando, setCarregando] = useState(true);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");
  const [sucesso, setSucesso] = useState("");
  const [codigo, setCodigo] = useState(null);

  const carregar = useCallback(async () => {
    setErro("");
    try {
      const { data } = await obterConfiguracaoTelegram();
      setConfig(data);
    } catch (e) {
      setErro(extrairMensagemErro(e));
    } finally {
      setCarregando(false);
    }
  }, []);

  useEffect(() => {
    carregar();
  }, [carregar]);

  async function handleGerarCodigo() {
    setErro("");
    setSucesso("");
    setSalvando(true);
    try {
      const { data } = await gerarCodigoTelegram();
      setCodigo(data);
      setSucesso("Código gerado! Envie a mensagem abaixo para o bot.");
    } catch (e) {
      setErro(extrairMensagemErro(e));
    } finally {
      setSalvando(false);
    }
  }

  async function handleSalvar(e) {
    e.preventDefault();
    if (!config) return;
    setSalvando(true);
    setErro("");
    setSucesso("");
    try {
      const { data } = await atualizarConfiguracaoTelegram({
        telegram_ativo: config.telegram_ativo,
        notificar_24h: config.notificar_24h,
        notificar_2h: config.notificar_2h,
      });
      setConfig(data);
      setSucesso("Configurações salvas.");
    } catch (e) {
      setErro(extrairMensagemErro(e));
    } finally {
      setSalvando(false);
    }
  }

  async function handleDesconectar() {
    if (!window.confirm("Desconectar o Telegram desta conta?")) return;
    setSalvando(true);
    setErro("");
    try {
      await desconectarTelegram();
      setCodigo(null);
      await carregar();
      setSucesso("Telegram desconectado.");
    } catch (e) {
      setErro(extrairMensagemErro(e));
    } finally {
      setSalvando(false);
    }
  }

  if (carregando) {
    return <p className="shell-muted">Carregando Telegram…</p>;
  }

  const conectado = config?.conectado;
  const botUser = config?.bot_username;
  const linkBot = botUser ? `https://t.me/${botUser}` : null;

  return (
    <section className="shell-perfil-card shell-perfil-telegram">
      <header className="shell-perfil-telegram-head">
        <MessageCircle size={20} />
        <div>
          <h2>Telegram</h2>
          <p>Receba lembretes das suas tarefas diretamente no Telegram.</p>
        </div>
      </header>

      <p className="shell-perfil-telegram-status">
        Status:{" "}
        <span className={conectado ? "is-on" : "is-off"}>
          {conectado ? "● Conectado" : "○ Não conectado"}
        </span>
        {config?.telegram_username ? ` (@${config.telegram_username})` : ""}
      </p>

      {erro && (
        <div className="shell-alert" role="alert">
          {erro}
        </div>
      )}
      {sucesso && <p className="shell-success-msg">{sucesso}</p>}

      {!conectado && (
        <div className="shell-perfil-telegram-connect">
          <button
            type="button"
            className="shell-btn-primary"
            onClick={handleGerarCodigo}
            disabled={salvando}
          >
            Conectar Telegram
          </button>

          {codigo && (
            <div className="shell-perfil-telegram-codigo">
              <p>
                Envie esta mensagem para o bot
                {botUser ? ` @${botUser}` : ""}:
              </p>
              <code>/conectar {codigo.codigo}</code>
              <p className="shell-muted">
                O código expira em {codigo.expira_em_minutos} minutos.
              </p>
              {linkBot && (
                <a
                  href={linkBot}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="shell-btn-ghost shell-perfil-telegram-link"
                >
                  <ExternalLink size={16} />
                  Abrir Telegram
                </a>
              )}
            </div>
          )}
        </div>
      )}

      {conectado && config && (
        <form onSubmit={handleSalvar} className="shell-perfil-telegram-form">
          <p className="shell-success-inline">✅ Telegram conectado</p>
          <label className="shell-check-row">
            <input
              type="checkbox"
              checked={config.notificar_24h}
              onChange={(e) =>
                setConfig((c) => ({ ...c, notificar_24h: e.target.checked }))
              }
            />
            Avisar 24 horas antes
          </label>
          <label className="shell-check-row">
            <input
              type="checkbox"
              checked={config.notificar_2h}
              onChange={(e) =>
                setConfig((c) => ({ ...c, notificar_2h: e.target.checked }))
              }
            />
            Avisar 2 horas antes
          </label>
          <label className="shell-check-row">
            <input
              type="checkbox"
              checked={config.telegram_ativo}
              onChange={(e) =>
                setConfig((c) => ({ ...c, telegram_ativo: e.target.checked }))
              }
            />
            Notificações ativas
          </label>
          <div className="shell-perfil-telegram-actions">
            <button type="submit" className="shell-btn-primary" disabled={salvando}>
              {salvando ? "Salvando…" : "Salvar configurações"}
            </button>
            <button
              type="button"
              className="shell-btn-danger-outline"
              onClick={handleDesconectar}
              disabled={salvando}
            >
              Desconectar Telegram
            </button>
          </div>
        </form>
      )}
    </section>
  );
}
