import { useMemo, useSyncExternalStore } from "react";
import { obterCoresGrafico } from "../utils/tema";

function subscribe(onStoreChange) {
  const observer = new MutationObserver(onStoreChange);
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["data-theme"],
  });
  window.addEventListener("storage", onStoreChange);
  return () => {
    observer.disconnect();
    window.removeEventListener("storage", onStoreChange);
  };
}

function getSnapshot() {
  return document.documentElement.getAttribute("data-theme") || "escuro";
}

export function useTema() {
  return useSyncExternalStore(subscribe, getSnapshot, () => "escuro");
}

export function useCoresGrafico() {
  const tema = useTema();
  return useMemo(() => obterCoresGrafico(), [tema]);
}
