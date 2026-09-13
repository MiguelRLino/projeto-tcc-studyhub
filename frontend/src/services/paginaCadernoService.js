import { api } from "./api";

export function listarPaginas(cadernoId) {
  return api.get(`/api/cadernos/${cadernoId}/paginas/`);
}

export function criarPagina(cadernoId, payload) {
  return api.post(`/api/cadernos/${cadernoId}/paginas/`, payload);
}

export function obterPagina(id) {
  return api.get(`/api/paginas/${id}/`);
}

export function atualizarPagina(id, payload) {
  return api.patch(`/api/paginas/${id}/`, payload);
}

export function excluirPagina(id) {
  return api.delete(`/api/paginas/${id}/`);
}

export function duplicarPagina(id) {
  return api.post(`/api/paginas/${id}/duplicar/`);
}

export function moverPagina(id, cadernoDestinoId) {
  return api.post(`/api/paginas/${id}/mover/`, {
    caderno_destino_id: cadernoDestinoId,
  });
}

export function favoritarPagina(id, favorita) {
  return api.patch(`/api/paginas/${id}/favoritar/`, { favorita });
}

export function pesquisarPaginas(params) {
  return api.get("/api/paginas/pesquisar/", { params });
}

export function reordenarPaginas(cadernoId, ordens) {
  return api.post(`/api/cadernos/${cadernoId}/paginas/reordenar/`, { ordens });
}

export function uploadImagemPagina(paginaId, arquivo) {
  const form = new FormData();
  form.append("arquivo", arquivo);
  return api.post(`/api/paginas/${paginaId}/imagens/`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}

export function registrarExportacaoPdf(paginaId) {
  return api.post(`/api/paginas/${paginaId}/exportar-pdf/`);
}
