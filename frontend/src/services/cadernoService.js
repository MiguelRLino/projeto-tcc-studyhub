import { api } from "./api";

export function listarCadernos() {
  return api.get("/api/cadernos/");
}

export function pesquisarCadernos(q) {
  return api.get("/api/cadernos/pesquisar/", { params: { q } });
}

export function criarCaderno(payload) {
  return api.post("/api/cadernos/", payload);
}

export function atualizarCaderno(id, payload) {
  return api.patch(`/api/cadernos/${id}/`, payload);
}

export function excluirCaderno(id) {
  return api.delete(`/api/cadernos/${id}/`);
}

export function obterCaderno(id) {
  return api.get(`/api/cadernos/${id}/`);
}
