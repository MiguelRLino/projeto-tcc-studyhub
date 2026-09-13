import { api } from "./api";

export function enviarPergunta(pergunta) {
  return api.post("/api/assistente/perguntar/", { pergunta });
}

export function listarHistorico() {
  return api.get("/api/assistente/historico/");
}

export function obterConversa(id) {
  return api.get(`/api/assistente/historico/${id}/`);
}

export function excluirConversa(id) {
  return api.delete(`/api/assistente/historico/${id}/`);
}
