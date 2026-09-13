import { Link } from "react-router-dom";
import {
  ArrowRight,
  BarChart3,
  Bell,
  BookOpen,
  Calendar,
  CheckSquare,
  ChevronDown,
  Clock,
  FileText,
  GraduationCap,
  LayoutDashboard,
  LogOut,
  Search,
  Sparkles,
  Star,
  Target,
  Timer,
  User,
} from "lucide-react";
import "../styles/landing.css";

const PASSOS = [
  {
    num: 1,
    titulo: "Cadastre suas disciplinas",
    desc: "Organize matérias, professores e prioridades em um só lugar.",
    Icon: BookOpen,
    cor: "#6366f1",
    bg: "rgba(99, 102, 241, 0.15)",
  },
  {
    num: 2,
    titulo: "Planeje suas tarefas",
    desc: "Defina prazos, lembretes e acompanhe o que precisa ser feito.",
    Icon: CheckSquare,
    cor: "#ec4899",
    bg: "rgba(236, 72, 153, 0.15)",
  },
  {
    num: 3,
    titulo: "Estude com foco",
    desc: "Use sessões de estudo cronometradas para manter a concentração.",
    Icon: Timer,
    cor: "#38bdf8",
    bg: "rgba(56, 189, 248, 0.15)",
  },
  {
    num: 4,
    titulo: "Acompanhe seu progresso",
    desc: "Visualize horas estudadas, metas e evolução por disciplina.",
    Icon: BarChart3,
    cor: "#34d399",
    bg: "rgba(52, 211, 153, 0.15)",
  },
  {
    num: 5,
    titulo: "Alcance seus objetivos",
    desc: "Conquiste melhores resultados com organização e consistência.",
    Icon: Target,
    cor: "#fb923c",
    bg: "rgba(251, 146, 60, 0.15)",
  },
];

const RECURSOS = [
  {
    Icon: CheckSquare,
    texto: "Dashboard completo com visão geral das suas atividades",
    cor: "#6366f1",
  },
  {
    Icon: Calendar,
    texto: "Calendário integrado com prazos e provas",
    cor: "#ec4899",
  },
  {
    Icon: BarChart3,
    texto: "Relatórios detalhados de horas e desempenho",
    cor: "#38bdf8",
  },
  {
    Icon: Star,
    texto: "Metas personalizadas para cada disciplina",
    cor: "#34d399",
  },
];

const BARRAS_GRAFICO = [
  { dia: "Seg", pct: 42 },
  { dia: "Ter", pct: 68 },
  { dia: "Qua", pct: 55 },
  { dia: "Qui", pct: 82 },
  { dia: "Sex", pct: 48 },
  { dia: "Sáb", pct: 30 },
  { dia: "Dom", pct: 38 },
];

const ATIVIDADES = [
  {
    titulo: "Concluiu exercícios de Álgebra",
    tag: "Matemática",
    tempo: "2h atrás",
    cor: "#34d399",
  },
  {
    titulo: "Estudou Revolução Francesa",
    tag: "História",
    tempo: "5h atrás",
    cor: "#fb923c",
  },
  {
    titulo: "Fez simulado de Mecânica",
    tag: "Física",
    tempo: "Ontem",
    cor: "#60a5fa",
  },
  {
    titulo: "Revisou Tabela Periódica",
    tag: "Química",
    tempo: "Ontem",
    cor: "#a78bfa",
  },
];

const ICONES_FUNDO = [
  BookOpen,
  CheckSquare,
  Clock,
  Calendar,
  FileText,
  Timer,
  BarChart3,
  GraduationCap,
];

function IlustracaoEstudante({ tipo }) {
  if (tipo === "esquerda") {
    return (
      <svg className="landing-char landing-char--left" viewBox="0 0 180 320" aria-hidden>
        <ellipse cx="90" cy="300" rx="70" ry="12" fill="rgba(0,0,0,0.25)" />
        <rect x="55" y="175" width="70" height="95" rx="18" fill="#6366f1" />
        <rect x="62" y="265" width="24" height="48" rx="10" fill="#1e1b4b" />
        <rect x="94" y="265" width="24" height="48" rx="10" fill="#1e1b4b" />
        <circle cx="90" cy="118" r="34" fill="#fcd9bd" />
        <path d="M56 98 Q90 62 124 98 L124 130 Q90 148 56 130 Z" fill="#312e81" />
        <rect x="118" y="188" width="38" height="52" rx="6" fill="#818cf8" />
        <rect x="124" y="194" width="26" height="8" rx="2" fill="#c7d2fe" />
      </svg>
    );
  }

  return (
    <svg className="landing-char landing-char--right" viewBox="0 0 200 320" aria-hidden>
      <ellipse cx="100" cy="300" rx="72" ry="12" fill="rgba(0,0,0,0.25)" />
      <rect x="68" y="178" width="64" height="92" rx="16" fill="#4f46e5" />
      <rect x="74" y="265" width="22" height="46" rx="9" fill="#312e81" />
      <rect x="104" y="265" width="22" height="46" rx="9" fill="#312e81" />
      <circle cx="100" cy="116" r="32" fill="#fcd9bd" />
      <path d="M68 96 Q100 58 132 96 L132 128 Q100 142 68 128 Z" fill="#4338ca" />
      <rect x="42" y="188" width="52" height="34" rx="6" fill="#1e1b4b" />
      <rect x="48" y="194" width="40" height="22" rx="3" fill="#6366f1" />
      <rect x="148" y="248" width="28" height="36" rx="8" fill="#6366f1" />
      <ellipse cx="162" cy="244" rx="18" ry="10" fill="#34d399" />
    </svg>
  );
}

function DashboardPreview({ className = "" }) {
  return (
    <div className={`landing-preview ${className}`.trim()} aria-hidden>
      <aside className="landing-preview__sidebar">
        <div className="landing-preview__brand">
          <div className="landing-preview__brand-icon">
            <GraduationCap size={20} />
          </div>
          <div>
            <strong>StudyHub</strong>
            <span>Organize seus estudos</span>
          </div>
        </div>
        <nav className="landing-preview__nav">
          <span className="landing-preview__nav-item landing-preview__nav-item--active">
            <LayoutDashboard size={16} /> Dashboard
          </span>
          <span className="landing-preview__nav-item">
            <BookOpen size={16} /> Disciplinas
          </span>
          <span className="landing-preview__nav-item">
            <CheckSquare size={16} /> Tarefas
          </span>
          <span className="landing-preview__nav-item">
            <Timer size={16} /> Sessões de Estudo
          </span>
          <span className="landing-preview__nav-item">
            <BarChart3 size={16} /> Relatórios
          </span>
          <span className="landing-preview__nav-item">
            <User size={16} /> Perfil
          </span>
        </nav>
        <span className="landing-preview__nav-item landing-preview__nav-item--logout">
          <LogOut size={16} /> Sair
        </span>
      </aside>

      <div className="landing-preview__main">
        <div className="landing-preview__topbar">
          <div className="landing-preview__search">
            <Search size={15} />
            <span>Buscar algo...</span>
          </div>
          <div className="landing-preview__user">
            <Bell size={18} />
            <div className="landing-preview__avatar">JS</div>
            <div className="landing-preview__user-text">
              <strong>João Silva</strong>
              <span>Estudante</span>
            </div>
            <ChevronDown size={16} />
          </div>
        </div>

        <div className="landing-preview__content">
          <header className="landing-preview__head">
            <h2>Dashboard</h2>
            <p>Bem-vindo de volta! Aqui está um resumo das suas atividades.</p>
          </header>

          <div className="landing-preview__stats">
            <article>
              <CheckSquare size={18} color="#60a5fa" />
              <h3>Tarefas pendentes</h3>
              <p className="landing-preview__stat-value">12</p>
              <span className="landing-preview__stat-hint up">↗ 4 novas hoje</span>
            </article>
            <article>
              <Clock size={18} color="#6366f1" />
              <h3>Horas estudadas</h3>
              <p className="landing-preview__stat-value">27h</p>
              <span className="landing-preview__stat-hint up">↗ Essa semana</span>
            </article>
            <article>
              <BookOpen size={18} color="#60a5fa" />
              <h3>Disciplinas ativas</h3>
              <p className="landing-preview__stat-value">8</p>
              <span className="landing-preview__stat-hint">2 em alta prioridade</span>
            </article>
            <article>
              <Calendar size={18} color="#fb923c" />
              <h3>Próxima prova</h3>
              <p className="landing-preview__stat-value">3 dias</p>
              <span className="landing-preview__stat-hint">Matemática — Cap. 5</span>
            </article>
          </div>

          <div className="landing-preview__grid">
            <article className="landing-preview__card">
              <h3>Horas de Estudo</h3>
              <div className="landing-preview__chart">
                {BARRAS_GRAFICO.map((barra) => (
                  <div key={barra.dia} className="landing-preview__bar-wrap">
                    <div
                      className="landing-preview__bar"
                      style={{ height: `${barra.pct}%` }}
                    />
                    <span>{barra.dia}</span>
                  </div>
                ))}
              </div>
            </article>

            <article className="landing-preview__card">
              <div className="landing-preview__card-head">
                <h3>Atividades Recentes</h3>
                <span>Ver todas</span>
              </div>
              <ul className="landing-preview__activities">
                {ATIVIDADES.map((item) => (
                  <li key={item.titulo}>
                    <span
                      className="landing-preview__dot"
                      style={{ background: item.cor }}
                    />
                    <div>
                      <strong>{item.titulo}</strong>
                      <span>
                        {item.tag} · {item.tempo}
                      </span>
                    </div>
                  </li>
                ))}
              </ul>
            </article>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function LandingPage() {
  return (
    <div className="landing-page">
      <div className="landing-bg-icons" aria-hidden>
        {ICONES_FUNDO.map((Icone, i) => (
          <Icone key={i} size={22} className={`landing-bg-icon landing-bg-icon--${i + 1}`} />
        ))}
      </div>

      <header className="landing-header">
        <Link to="/" className="landing-logo">
          <div className="landing-logo__icon">
            <GraduationCap size={22} />
          </div>
          <div>
            <strong>StudyHub</strong>
            <span>Organize seus estudos</span>
          </div>
        </Link>

        <nav className="landing-nav">
          <a href="#como-funciona">Como funciona</a>
          <Link to="/login">Entrar</Link>
          <Link to="/cadastro" className="landing-btn landing-btn--primary">
            Começar agora
          </Link>
        </nav>
      </header>

      <main>
        <section className="landing-hero">
          <h1>
            Descubra como uma organização{" "}
            <span className="landing-gradient landing-gradient--pink">eficiente</span> pode{" "}
            <span className="landing-gradient landing-gradient--blue">transformar</span> seus
            estudos
          </h1>
          <p>
            Planeje, acompanhe e conquiste seus objetivos acadêmicos com mais foco, disciplina e
            produtividade.
          </p>
        </section>

        <section className="landing-showcase">
          <IlustracaoEstudante tipo="esquerda" />
          <DashboardPreview />
          <IlustracaoEstudante tipo="direita" />
        </section>

        <section id="como-funciona" className="landing-how">
          <h2>
            Como funciona o <span className="landing-how__brand">StudyHub</span>
          </h2>
          <p className="landing-how__lead">
            Um fluxo simples para organizar matérias, focar nos estudos e acompanhar seu
            desempenho — tudo em uma plataforma pensada para estudantes.
          </p>

          <div className="landing-how__flow">
            {PASSOS.map((passo) => (
              <article key={passo.num} className="landing-how__card">
                <span
                  className="landing-how__badge"
                  style={{
                    background: passo.cor,
                    boxShadow: `0 0 0 4px #0b0d17, 0 4px 16px ${passo.cor}55`,
                  }}
                >
                  {passo.num}
                </span>
                <div
                  className="landing-how__icon"
                  style={{ background: passo.bg, color: passo.cor }}
                >
                  <passo.Icon size={22} strokeWidth={1.75} />
                </div>
                <h3>{passo.titulo}</h3>
                <p>{passo.desc}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="landing-features">
          <div className="landing-features__content">
            <span className="landing-pill">Tudo que você precisa</span>
            <h2>Organização inteligente para resultados reais</h2>
            <p>
              Ferramentas pensadas para simplificar sua rotina de estudos e ajudar você a manter
              foco, disciplina e produtividade todos os dias.
            </p>
            <ul className="landing-features__list">
              {RECURSOS.map(({ Icon, texto, cor }) => (
                <li key={texto}>
                  <span className="landing-features__list-icon" style={{ color: cor }}>
                    <Icon size={18} />
                  </span>
                  {texto}
                </li>
              ))}
            </ul>
            <Link to="/cadastro" className="landing-btn landing-btn--gradient">
              Começar gratuitamente
              <ArrowRight size={18} />
            </Link>
          </div>
          <div className="landing-features__preview">
            <DashboardPreview className="landing-preview--feature" />
          </div>
        </section>

        <section className="landing-cta-banner">
          <div className="landing-cta-banner__text">
            <div className="landing-cta-banner__icon">
              <Sparkles size={22} />
            </div>
            <div>
              <strong>Pronto para transformar sua forma de estudar?</strong>
              <p>
                Junte-se a estudantes que já organizam tarefas, sessões e metas com o StudyHub.
              </p>
            </div>
          </div>
          <Link to="/cadastro" className="landing-btn landing-btn--gradient">
            Começar agora
            <ArrowRight size={18} />
          </Link>
        </section>
      </main>

      <footer className="landing-footer">
        <p>© 2026 StudyHub. Todos os direitos reservados.</p>
      </footer>
    </div>
  );
}
