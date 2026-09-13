import { api } from "./api";

export function obterResumoSessoes() {
  return api.get("/api/sessoes-estudo/resumo/");
}

export function listarSessoes() {
  return api.get("/api/sessoes-estudo/");
}

export function criarSessao(payload) {
  return api.post("/api/sessoes-estudo/", payload);
}
