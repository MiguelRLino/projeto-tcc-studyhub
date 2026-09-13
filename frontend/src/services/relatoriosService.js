import { api } from "./api";

export function obterResumoRelatorios() {
  return api.get("/api/relatorios/resumo/");
}
