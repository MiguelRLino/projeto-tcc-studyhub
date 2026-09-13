import { api } from "./api";

export function obterConfiguracaoTelegram() {
  return api.get("/api/telegram/configuracao/");
}

export function gerarCodigoTelegram() {
  return api.post("/api/telegram/gerar-codigo/");
}

export function atualizarConfiguracaoTelegram(payload) {
  return api.patch("/api/telegram/configuracao/", payload);
}

export function desconectarTelegram() {
  return api.delete("/api/telegram/desconectar/");
}
