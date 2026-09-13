import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { NavLink, useNavigate, useParams } from "react-router-dom";
import {
  BookMarked,
  ChevronDown,
  ChevronRight,
  FilePlus,
  FolderPlus,
  GripVertical,
  Search,
  Star,
} from "lucide-react";
import { extrairMensagemErro } from "../../services/api";
import { listarCadernos, pesquisarCadernos } from "../../services/cadernoService";
import {
  listarPaginas,
  pesquisarPaginas,
  reordenarPaginas,
} from "../../services/paginaCadernoService";

function debounce(fn, ms) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), ms);
  };
}

export default function CadernosSidebar({
  onNovoCaderno,
  onEditarCaderno,
  onNovaPagina,
  recarregarToken = 0,
}) {
  const { cadernoId, paginaId } = useParams();
  const navigate = useNavigate();
  const [cadernos, setCadernos] = useState([]);
  const [paginasMap, setPaginasMap] = useState({});
  const [expandidos, setExpandidos] = useState({});
  const [favoritas, setFavoritas] = useState([]);
  const [busca, setBusca] = useState("");
  const [resultados, setResultados] = useState(null);
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(true);
  const dragRef = useRef(null);

  const carregarCadernos = useCallback(async () => {
    setErro("");
    try {
      const { data } = await listarCadernos();
      setCadernos(Array.isArray(data) ? data : []);
    } catch (e) {
      setErro(extrairMensagemErro(e));
    } finally {
      setCarregando(false);
    }
  }, []);

  const carregarFavoritas = useCallback(async () => {
    try {
      const { data } = await pesquisarPaginas({ favoritas: "1" });
      setFavoritas(Array.isArray(data) ? data : []);
    } catch {
      setFavoritas([]);
    }
  }, []);

  const carregarPaginas = useCallback(async (id) => {
    try {
      const { data } = await listarPaginas(id);
      setPaginasMap((prev) => ({
        ...prev,
        [id]: Array.isArray(data) ? data : [],
      }));
    } catch {
      setPaginasMap((prev) => ({ ...prev, [id]: [] }));
    }
  }, []);

  useEffect(() => {
    carregarCadernos();
    carregarFavoritas();
  }, [carregarCadernos, carregarFavoritas, recarregarToken]);

  useEffect(() => {
    if (cadernoId) {
      setExpandidos((prev) => ({ ...prev, [cadernoId]: true }));
      carregarPaginas(cadernoId);
    }
  }, [cadernoId, carregarPaginas, recarregarToken]);

  const buscarDebounced = useMemo(
    () =>
      debounce(async (q) => {
        const termo = q.trim();
        if (!termo) {
          setResultados(null);
          return;
        }
        try {
          const [cRes, pRes] = await Promise.all([
            pesquisarCadernos(termo),
            pesquisarPaginas({ q: termo }),
          ]);
          setResultados({
            cadernos: Array.isArray(cRes.data) ? cRes.data : [],
            paginas: Array.isArray(pRes.data) ? pRes.data : [],
          });
        } catch {
          setResultados({ cadernos: [], paginas: [] });
        }
      }, 350),
    [],
  );

  useEffect(() => {
    buscarDebounced(busca);
  }, [busca, buscarDebounced]);

  function toggleExpandir(id) {
    setExpandidos((prev) => {
      const aberto = !prev[id];
      if (aberto && !paginasMap[id]) carregarPaginas(id);
      return { ...prev, [id]: aberto };
    });
  }

  async function handleDrop(cadernoAlvoId, paginaArrastadaId) {
    const paginas = paginasMap[cadernoAlvoId] || [];
    const ids = paginas.map((p) => p.id_pagina);
    const fromIdx = ids.indexOf(paginaArrastadaId);
    const toIdx = ids.indexOf(dragRef.current?.overId);
    if (fromIdx < 0 || toIdx < 0 || fromIdx === toIdx) return;

    const nova = [...paginas];
    const [item] = nova.splice(fromIdx, 1);
    nova.splice(toIdx, 0, item);
    const ordens = nova.map((p, i) => ({ id_pagina: p.id_pagina, ordem: i + 1 }));
    setPaginasMap((prev) => ({ ...prev, [cadernoAlvoId]: nova }));
    try {
      await reordenarPaginas(cadernoAlvoId, ordens);
    } catch {
      carregarPaginas(cadernoAlvoId);
    }
  }

  function renderPaginas(caderno) {
    const paginas = paginasMap[caderno.id_caderno] || [];
    return paginas.map((p) => (
      <div
        key={p.id_pagina}
        className="caderno-sidebar-pagina-wrap"
        draggable
        onDragStart={() => {
          dragRef.current = { id: p.id_pagina, cadernoId: caderno.id_caderno };
        }}
        onDragOver={(e) => {
          e.preventDefault();
          dragRef.current = { ...dragRef.current, overId: p.id_pagina };
        }}
        onDrop={(e) => {
          e.preventDefault();
          if (dragRef.current?.cadernoId === caderno.id_caderno) {
            handleDrop(caderno.id_caderno, dragRef.current.id);
          }
        }}
      >
        <GripVertical size={12} className="caderno-drag-handle" />
        <NavLink
          to={`/cadernos/${caderno.id_caderno}/paginas/${p.id_pagina}`}
          className={({ isActive }) =>
            `caderno-sidebar-pagina${isActive ? " is-active" : ""}`
          }
        >
          {p.favorita && <Star size={12} className="caderno-star-inline" />}
          {p.titulo}
        </NavLink>
      </div>
    ));
  }

  return (
    <aside className="caderno-sidebar">
      <div className="caderno-sidebar-header">
        <BookMarked size={18} />
        <strong>Caderno Digital</strong>
      </div>

      <div className="caderno-sidebar-actions">
        <button type="button" className="caderno-sidebar-btn" onClick={onNovoCaderno}>
          <FolderPlus size={16} />
          Novo caderno
        </button>
      </div>

      <div className="caderno-sidebar-search">
        <Search size={16} />
        <input
          type="search"
          placeholder="Buscar cadernos e páginas…"
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
        />
      </div>

      {erro && <p className="caderno-erro caderno-erro--sm">{erro}</p>}

      {resultados ? (
        <div className="caderno-sidebar-section">
          <h4>Resultados</h4>
          {resultados.cadernos.length === 0 && resultados.paginas.length === 0 && (
            <p className="caderno-muted">Nenhum resultado.</p>
          )}
          {resultados.cadernos.map((c) => (
            <button
              key={c.id_caderno}
              type="button"
              className="caderno-sidebar-item"
              onClick={() => navigate(`/cadernos/${c.id_caderno}`)}
            >
              {c.titulo}
            </button>
          ))}
          {resultados.paginas.map((p) => (
            <NavLink
              key={p.id_pagina}
              to={`/cadernos/${p.id_caderno}/paginas/${p.id_pagina}`}
              className="caderno-sidebar-pagina"
              onClick={() => setBusca("")}
            >
              {p.titulo}
              <span className="caderno-muted">{p.caderno_titulo}</span>
            </NavLink>
          ))}
        </div>
      ) : (
        <>
          {favoritas.length > 0 && (
            <div className="caderno-sidebar-section">
              <h4>
                <Star size={14} /> Favoritos
              </h4>
              {favoritas.map((p) => (
                <NavLink
                  key={p.id_pagina}
                  to={`/cadernos/${p.id_caderno}/paginas/${p.id_pagina}`}
                  className={({ isActive }) =>
                    `caderno-sidebar-pagina${isActive ? " is-active" : ""}`
                  }
                >
                  {p.titulo}
                </NavLink>
              ))}
            </div>
          )}

          <div className="caderno-sidebar-section">
            <h4>Meus cadernos</h4>
            {carregando && <p className="caderno-muted">Carregando…</p>}
            {!carregando && cadernos.length === 0 && (
              <p className="caderno-muted">Nenhum caderno ainda.</p>
            )}
            {cadernos.map((c) => {
              const aberto = expandidos[c.id_caderno];
              const ativo = String(c.id_caderno) === cadernoId;
              return (
                <div key={c.id_caderno} className="caderno-sidebar-caderno">
                  <div className={`caderno-sidebar-caderno-head${ativo ? " is-active" : ""}`}>
                    <button
                      type="button"
                      className="caderno-expand"
                      onClick={() => toggleExpandir(c.id_caderno)}
                    >
                      {aberto ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                    </button>
                    <button
                      type="button"
                      className="caderno-sidebar-caderno-titulo"
                      style={{ borderLeftColor: c.cor || "#6366f1" }}
                      onClick={() => {
                        toggleExpandir(c.id_caderno);
                        navigate(`/cadernos/${c.id_caderno}`);
                      }}
                    >
                      {c.titulo}
                      <span className="caderno-badge">{c.total_paginas ?? 0}</span>
                    </button>
                    <button
                      type="button"
                      className="caderno-icon-btn sm"
                      title="Editar caderno"
                      onClick={() => onEditarCaderno(c)}
                    >
                      ✎
                    </button>
                    <button
                      type="button"
                      className="caderno-icon-btn sm"
                      title="Nova página"
                      onClick={() => onNovaPagina(c)}
                    >
                      <FilePlus size={14} />
                    </button>
                  </div>
                  {aberto && (
                    <div className="caderno-sidebar-paginas">{renderPaginas(c)}</div>
                  )}
                </div>
              );
            })}
          </div>
        </>
      )}
    </aside>
  );
}
