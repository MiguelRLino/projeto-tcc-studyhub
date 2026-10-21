const TOKEN_KEY = "access_token";
const USER_KEY = "aluno";
const TIPO_KEY = "tipo_usuario";

export const TIPO_ALUNO = "ALUNO";
export const TIPO_RESPONSAVEL = "RESPONSAVEL";

export function salvarSessao(access, usuario, tipo = TIPO_ALUNO) {
  localStorage.setItem(TOKEN_KEY, access);
  localStorage.setItem(USER_KEY, JSON.stringify(usuario));
  localStorage.setItem(TIPO_KEY, tipo || TIPO_ALUNO);
}

export function limparSessao() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  localStorage.removeItem(TIPO_KEY);
}

export function obterToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function obterAluno() {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function obterUsuario() {
  return obterAluno();
}

export function obterTipoUsuario() {
  return localStorage.getItem(TIPO_KEY) || TIPO_ALUNO;
}

export function ehResponsavel() {
  return obterTipoUsuario() === TIPO_RESPONSAVEL;
}

export function ehAluno() {
  return obterTipoUsuario() === TIPO_ALUNO;
}

export function estaAutenticado() {
  return Boolean(obterToken());
}

export function atualizarAlunoLocal(aluno) {
  if (!aluno) return;
  localStorage.setItem(USER_KEY, JSON.stringify(aluno));
}

export function destinoPosLogin(tipo, from) {
  if (tipo === TIPO_RESPONSAVEL) {
    if (from && String(from).startsWith("/responsavel")) return from;
    if (from && String(from).startsWith("/convite/")) return from;
    return "/responsavel";
  }
  if (from && from !== "/login" && !String(from).startsWith("/responsavel")) {
    return from;
  }
  return "/dashboard";
}
