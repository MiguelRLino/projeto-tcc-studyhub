import { api } from "./api";

export function listarMeusResponsaveis() {
  return api.get("/api/responsaveis/meus-responsaveis/");
}

export function convidarResponsavel(payload) {
  return api.post("/api/responsaveis/convidar/", payload);
}

export function reenviarConvite(conviteId) {
  return api.post(`/api/responsaveis/convites/${conviteId}/reenviar/`);
}

export function cancelarConvite(conviteId) {
  return api.delete(`/api/responsaveis/convites/${conviteId}/`);
}

export function removerVinculo(vinculoId) {
  return api.delete(`/api/responsaveis/vinculos/${vinculoId}/`);
}

export function validarConvite(token) {
  return api.get(`/api/responsaveis/convites/validar/${encodeURIComponent(token)}/`);
}

export function aceitarConvite(payload) {
  return api.post("/api/responsaveis/convites/aceitar/", payload);
}

export function listarMeusAlunos() {
  return api.get("/api/responsaveis/meus-alunos/");
}

export function obterDashboardAluno(alunoId) {
  return api.get(`/api/responsaveis/alunos/${alunoId}/dashboard/`);
}

export function obterTarefasAluno(alunoId) {
  return api.get(`/api/responsaveis/alunos/${alunoId}/tarefas/`);
}

export function obterDisciplinasAluno(alunoId) {
  return api.get(`/api/responsaveis/alunos/${alunoId}/disciplinas/`);
}

export function obterSessoesAluno(alunoId) {
  return api.get(`/api/responsaveis/alunos/${alunoId}/sessoes/`);
}

export function obterRelatoriosAluno(alunoId) {
  return api.get(`/api/responsaveis/alunos/${alunoId}/relatorios/`);
}
