/** Texto curto em português para diferença até uma data ISO. */
export function tempoRelativo(iso) {
  if (!iso) return "";
  const alvo = new Date(iso).getTime();
  if (Number.isNaN(alvo)) return "";
  let seg = Math.round((Date.now() - alvo) / 1000);
  if (seg < 45) return "agora há pouco";
  const min = Math.floor(seg / 60);
  if (min < 60) return min <= 1 ? "há 1 minuto" : `há ${min} minutos`;
  const h = Math.floor(min / 60);
  if (h < 24) return h === 1 ? "há 1 hora" : `há ${h} horas`;
  const d = Math.floor(h / 24);
  if (d < 7) return d === 1 ? "há 1 dia" : `há ${d} dias`;
  const sem = Math.floor(d / 7);
  if (sem < 5) return sem === 1 ? "há 1 semana" : `há ${sem} semanas`;
  const mes = Math.floor(d / 30);
  return mes <= 1 ? "há cerca de 1 mês" : `há ${mes} meses`;
}
