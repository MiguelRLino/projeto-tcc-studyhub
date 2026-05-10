import { GraduationCap } from "lucide-react";
import "../styles/auth.css";

export default function AuthShell({ title, subtitle, children }) {
  return (
    <div className="auth-page">
      <div className="auth-center">
        <header className="auth-brand">
          <div className="auth-logo" aria-hidden>
            <GraduationCap size={28} strokeWidth={2} />
          </div>
          <h1 className="auth-title">{title}</h1>
          <p className="auth-subtitle">{subtitle}</p>
        </header>
        <div className="auth-card">{children}</div>
        <p className="auth-copyright">© 2026 StudyHub. Todos os direitos reservados.</p>
      </div>
    </div>
  );
}
