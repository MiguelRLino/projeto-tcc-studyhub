import { api } from "./api";

export function solicitarRecuperacaoSenha(email) {
  return api.post("/api/alunos/recuperar-senha/solicitar/", { email });
}

export function confirmarNovaSenha(token, senhaNova) {
  return api.post("/api/alunos/recuperar-senha/confirmar/", {
    token,
    senha_nova: senhaNova,
  });
}
