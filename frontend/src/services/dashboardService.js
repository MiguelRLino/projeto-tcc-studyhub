import { api } from "./api";

export function obterResumoDashboard() {
  return api.get("/api/dashboard/resumo/");
}
