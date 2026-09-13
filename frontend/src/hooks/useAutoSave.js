import { useCallback, useEffect, useRef, useState } from "react";

/**
 * Autosave com debounce e controle de concorrência (ignora respostas antigas).
 */
export function useAutoSave(salvarFn, delayMs = 2000) {
  const [estado, setEstado] = useState("idle");
  const timerRef = useRef(null);
  const seqRef = useRef(0);
  const ultimoSalvoRef = useRef(null);

  const cancelar = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const disparar = useCallback(
    (payload, { imediato = false } = {}) => {
      const chave = JSON.stringify(payload);
      if (chave === ultimoSalvoRef.current && !imediato) {
        return Promise.resolve();
      }

      cancelar();

      const executar = async () => {
        const seq = ++seqRef.current;
        setEstado("salvando");
        try {
          await salvarFn(payload);
          if (seq !== seqRef.current) return;
          ultimoSalvoRef.current = chave;
          setEstado("salvo");
        } catch {
          if (seq !== seqRef.current) return;
          setEstado("erro");
        }
      };

      if (imediato) {
        return executar();
      }

      timerRef.current = setTimeout(executar, delayMs);
      return Promise.resolve();
    },
    [salvarFn, delayMs, cancelar],
  );

  const resetUltimoSalvo = useCallback(() => {
    ultimoSalvoRef.current = null;
  }, []);

  useEffect(() => cancelar, [cancelar]);

  return { estado, disparar, resetUltimoSalvo };
}
