/** Métricas de texto a partir do JSON do Tiptap. */

export function extrairTextoConteudo(conteudo) {
  const partes = [];
  function walk(node) {
    if (!node || typeof node !== "object") return;
    if (node.type === "text" && node.text) partes.push(node.text);
    (node.content || []).forEach(walk);
  }
  walk(conteudo && conteudo.type === "doc" ? conteudo : { type: "doc", content: [] });
  return partes.join(" ").trim();
}

export function calcularMetricas(conteudo) {
  const texto = extrairTextoConteudo(conteudo);
  if (!texto) return { palavras: 0, caracteres: 0, leituraMin: 0 };
  const caracteres = texto.length;
  const palavras = texto.split(/\s+/).filter(Boolean).length;
  const leituraMin = palavras <= 0 ? 0 : Math.max(1, Math.round(palavras / 200));
  return { palavras, caracteres, leituraMin };
}

export const CONTEUDO_VAZIO = {
  type: "doc",
  content: [{ type: "paragraph" }],
};

export function normalizarConteudo(conteudo) {
  if (conteudo && typeof conteudo === "object" && conteudo.type === "doc") {
    return conteudo;
  }
  return CONTEUDO_VAZIO;
}
