import { api } from "./api";

export function obterCalendario(ano, mes) {
  return api.get("/api/calendario/", { params: { ano, mes } });
}

export function criarTarefa(payload) {
  return api.post("/api/tarefas/", payload);
}

export function criarSessaoPlanejada(payload) {
  return api.post("/api/sessoes-planejadas/", payload);
}

export function excluirSessaoPlanejada(id) {
  return api.delete(`/api/sessoes-planejadas/${id}/`);
}
