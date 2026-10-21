import { BrowserRouter, Route, Routes } from "react-router-dom";
import AppLayout from "./components/layout/AppLayout";
import RotaAluno from "./components/RotaAluno";
import RotaPrivada from "./components/RotaPrivada";
import RotaResponsavel from "./components/RotaResponsavel";
import Cadastro from "./pages/Cadastro";
import DashboardHome from "./pages/DashboardHome";
import DisciplinasPage from "./pages/DisciplinasPage";
import TarefasPage from "./pages/TarefasPage";
import RelatoriosPage from "./pages/RelatoriosPage";
import PerfilPage from "./pages/PerfilPage";
import SessoesEstudoPage from "./pages/SessoesEstudoPage";
import CalendarioPage from "./pages/CalendarioPage";
import EsqueciSenha from "./pages/EsqueciSenha";
import LandingPage from "./pages/LandingPage";
import Login from "./pages/Login";
import RedefinirSenha from "./pages/RedefinirSenha";
import CadernosLayout, {
  CadernosWelcome,
} from "./pages/CadernosLayout";
import EditorPage, { CadernoHubPage } from "./pages/EditorPage";
import AssistenteIAPage from "./pages/AssistenteIAPage";
import AceitarConviteResponsavel from "./pages/AceitarConviteResponsavel";
import ResponsavelDashboardPage from "./pages/ResponsavelDashboardPage";
import ResponsavelAlunosPage from "./pages/ResponsavelAlunosPage";
import ResponsavelPerfilPage from "./pages/ResponsavelPerfilPage";
import "./App.css";

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/cadastro" element={<Cadastro />} />
          <Route path="/login" element={<Login />} />
          <Route path="/esqueci-senha" element={<EsqueciSenha />} />
          <Route path="/redefinir-senha" element={<RedefinirSenha />} />
          <Route
            path="/convite/responsavel/:token"
            element={<AceitarConviteResponsavel />}
          />

          <Route element={<RotaPrivada />}>
            <Route element={<AppLayout />}>
              <Route element={<RotaAluno />}>
                <Route path="/dashboard" element={<DashboardHome />} />
                <Route path="/disciplinas" element={<DisciplinasPage />} />
                <Route path="/tarefas" element={<TarefasPage />} />
                <Route path="/sessoes" element={<SessoesEstudoPage />} />
                <Route path="/calendario" element={<CalendarioPage />} />
                <Route path="/relatorios" element={<RelatoriosPage />} />
                <Route path="/cadernos" element={<CadernosLayout />}>
                  <Route index element={<CadernosWelcome />} />
                  <Route path=":cadernoId" element={<CadernoHubPage />} />
                  <Route
                    path=":cadernoId/paginas/:paginaId"
                    element={<EditorPage />}
                  />
                </Route>
                <Route path="/assistente" element={<AssistenteIAPage />} />
                <Route path="/perfil" element={<PerfilPage />} />
              </Route>

              <Route element={<RotaResponsavel />}>
                <Route path="/responsavel" element={<ResponsavelDashboardPage />} />
                <Route
                  path="/responsavel/alunos"
                  element={<ResponsavelAlunosPage />}
                />
                <Route
                  path="/responsavel/alunos/:alunoId"
                  element={<ResponsavelDashboardPage />}
                />
                <Route
                  path="/responsavel/perfil"
                  element={<ResponsavelPerfilPage />}
                />
              </Route>
            </Route>
          </Route>

          <Route
            path="*"
            element={
              <main className="app-simple-page">
                <p>Página não encontrada.</p>
              </main>
            }
          />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
