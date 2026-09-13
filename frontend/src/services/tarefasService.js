import { api } from "./api";

export function listarTarefas(params) {
  return api.get("/api/tarefas/", { params });
}

export function criarTarefa(payload) {
  return api.post("/api/tarefas/", payload);
}

export function atualizarTarefa(idTarefa, payload) {
  return api.patch(`/api/tarefas/${idTarefa}/`, payload);
}

export function excluirTarefaLogico(idTarefa) {
  return api.delete(`/api/tarefas/${idTarefa}/`);
}
