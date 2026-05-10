import { api } from "./api";

export function listarDisciplinas() {
  return api.get("/api/disciplinas/");
}

export function criarDisciplina(payload) {
  return api.post("/api/disciplinas/", payload);
}

export function atualizarDisciplina(idDisciplina, payload) {
  return api.patch(`/api/disciplinas/${idDisciplina}/`, payload);
}

export function excluirDisciplinaLogico(idDisciplina) {
  return api.delete(`/api/disciplinas/${idDisciplina}/`);
}
