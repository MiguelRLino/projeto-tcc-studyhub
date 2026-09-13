import { api } from "./api";

export function obterPerfil() {
  return api.get("/api/alunos/me/");
}

export function atualizarPerfil(payload) {
  return api.patch("/api/alunos/me/", payload);
}

export function alterarSenha(payload) {
  return api.post("/api/alunos/me/senha/", payload);
}

export function excluirConta() {
  return api.delete("/api/alunos/me/");
}
