import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  BarChart3,
  BookMarked,
  BookOpen,
  CalendarDays,
  CheckSquare,
  Clock,
  GraduationCap,
  LayoutDashboard,
  LogOut,
  Sparkles,
  User,
} from "lucide-react";
import { limparSessao } from "../../services/authService";
import "../../styles/shell.css";

export default function AppLayout() {
  const navigate = useNavigate();

  function handleSair() {
    limparSessao();
    navigate("/login", { replace: true });
  }

  return (
    <div className="shell-root">
      <aside className="shell-sidebar">
        <div className="shell-brand">
          <div className="shell-brand-icon" aria-hidden>
            <GraduationCap size={22} strokeWidth={2} />
          </div>
          <div className="shell-brand-text">
            <strong>StudyHub</strong>
            <span>Organize seus estudos</span>
          </div>
        </div>

        <nav className="shell-nav">
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              isActive ? "shell-nav-active" : undefined
            }
            end
          >
            <LayoutDashboard size={18} />
            Dashboard
          </NavLink>
          <NavLink
            to="/disciplinas"
            className={({ isActive }) =>
              isActive ? "shell-nav-active" : undefined
            }
          >
            <BookOpen size={18} />
            Disciplinas
          </NavLink>
          <NavLink
            to="/tarefas"
            className={({ isActive }) =>
              isActive ? "shell-nav-active" : undefined
            }
          >
            <CheckSquare size={18} />
            Tarefas
          </NavLink>
          <NavLink
            to="/sessoes"
            className={({ isActive }) =>
              isActive ? "shell-nav-active" : undefined
            }
          >
            <Clock size={18} />
            Sessões de Estudo
          </NavLink>
          <NavLink
            to="/calendario"
            className={({ isActive }) =>
              isActive ? "shell-nav-active" : undefined
            }
          >
            <CalendarDays size={18} />
            Calendário
          </NavLink>
          <NavLink
            to="/relatorios"
            className={({ isActive }) =>
              isActive ? "shell-nav-active" : undefined
            }
          >
            <BarChart3 size={18} />
            Relatórios
          </NavLink>
          <NavLink
            to="/cadernos"
            className={({ isActive }) =>
              isActive ? "shell-nav-active" : undefined
            }
          >
            <BookMarked size={18} />
            Caderno Digital
          </NavLink>
          <NavLink
            to="/assistente"
            className={({ isActive }) =>
              isActive ? "shell-nav-active" : undefined
            }
          >
            <Sparkles size={18} />
            Assistente IA
          </NavLink>
          <NavLink
            to="/perfil"
            className={({ isActive }) =>
              isActive ? "shell-nav-active" : undefined
            }
          >
            <User size={18} />
            Perfil
          </NavLink>
        </nav>

        <div className="shell-nav-footer">
          <button type="button" className="linkish" onClick={handleSair}>
            <LogOut size={18} />
            Sair
          </button>
        </div>
      </aside>

      <main className="shell-main">
        <Outlet />
      </main>
    </div>
  );
}
