import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  BarChart3,
  BookOpen,
  CheckSquare,
  Clock,
  GraduationCap,
  LayoutDashboard,
  LogOut,
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
          <button type="button" className="linkish shell-nav-disabled" disabled title="Em breve">
            <CheckSquare size={18} />
            Tarefas
          </button>
          <button type="button" className="linkish shell-nav-disabled" disabled title="Em breve">
            <Clock size={18} />
            Sessões de Estudo
          </button>
          <button type="button" className="linkish shell-nav-disabled" disabled title="Em breve">
            <BarChart3 size={18} />
            Relatórios
          </button>
          <button type="button" className="linkish shell-nav-disabled" disabled title="Em breve">
            <User size={18} />
            Perfil
          </button>
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
