import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export const api = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
});

/** Rotas públicas: não enviar JWT velho (senão o backend pode falhar antes da view). */
function requisicaoPublicaSemAuth(config) {
  const url = `${config.baseURL || ""}${config.url || ""}`;
  return (
    url.includes("/api/alunos/login/google/") ||
    url.includes("/api/alunos/login/") ||
    url.includes("/api/alunos/cadastro/") ||
    url.includes("/api/alunos/recuperar-senha/")
  );
}

api.interceptors.request.use((config) => {
  if (requisicaoPublicaSemAuth(config)) {
    delete config.headers.Authorization;
    return config;
  }
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/**
 * Extrai mensagem legível de erro do backend (DRF / nosso handler).
 */
export function extrairMensagemErro(error) {
  const data = error.response?.data;
  if (!data) return error.message || "Erro de conexão. Tente novamente.";
  if (typeof data.erro === "string") return data.erro;
  if (data.erros) {
    const partes = [];
    for (const [campo, msgs] of Object.entries(data.erros)) {
      if (Array.isArray(msgs)) partes.push(`${campo}: ${msgs.join(" ")}`);
      else partes.push(`${campo}: ${msgs}`);
    }
    return partes.join(" ") || "Dados inválidos.";
  }
  if (typeof data.detail === "string") return data.detail;
  return "Não foi possível concluir a operação.";
}
