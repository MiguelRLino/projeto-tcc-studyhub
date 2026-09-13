const TOKEN_KEY = "access_token";
const USER_KEY = "aluno";

export function salvarSessao(access, aluno) {
  localStorage.setItem(TOKEN_KEY, access);
  localStorage.setItem(USER_KEY, JSON.stringify(aluno));
}

export function limparSessao() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
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

export function estaAutenticado() {
  return Boolean(obterToken());
}

export function atualizarAlunoLocal(aluno) {
  if (!aluno) return;
  localStorage.setItem(USER_KEY, JSON.stringify(aluno));
}
