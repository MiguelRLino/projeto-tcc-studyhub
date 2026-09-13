export const PREFS_KEY = "studyhub_prefs";
export const TEMA_ESCURO = "escuro";
export const TEMA_CLARO = "claro";

export function obterPreferencias() {
  try {
    const raw = JSON.parse(localStorage.getItem(PREFS_KEY) || "{}");
    return {
      notificacoes: raw.notificacoes !== false,
      tema: raw.tema === TEMA_CLARO ? TEMA_CLARO : TEMA_ESCURO,
    };
  } catch {
    return { notificacoes: true, tema: TEMA_ESCURO };
  }
}

export function salvarPreferencias(patch) {
  const next = { ...obterPreferencias(), ...patch };
  localStorage.setItem(PREFS_KEY, JSON.stringify(next));
  if (patch.tema) aplicarTema(patch.tema);
  return next;
}

export function aplicarTema(tema) {
  const root = document.documentElement;
  root.setAttribute("data-theme", tema === TEMA_CLARO ? TEMA_CLARO : TEMA_ESCURO);
}

export function aplicarTemaSalvo() {
  aplicarTema(obterPreferencias().tema);
}

export function obterCoresGrafico() {
  const claro = document.documentElement.getAttribute("data-theme") === TEMA_CLARO;
  if (claro) {
    return {
      grid: "#e5e7eb",
      tick: "#6b7280",
      tooltipBg: "#ffffff",
      tooltipBorder: "rgba(15, 23, 42, 0.1)",
      tooltipColor: "#111827",
    };
  }
  return {
    grid: "#2a2a35",
    tick: "#9ca3af",
    tooltipBg: "#16161e",
    tooltipBorder: "rgba(255,255,255,0.08)",
    tooltipColor: "#f9fafb",
  };
}
