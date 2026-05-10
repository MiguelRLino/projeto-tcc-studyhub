import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "./components/layout/AppLayout";
import RotaPrivada from "./components/RotaPrivada";
import Cadastro from "./pages/Cadastro";
import DashboardHome from "./pages/DashboardHome";
import DisciplinasPage from "./pages/DisciplinasPage";
import Login from "./pages/Login";
import "./App.css";

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Routes>
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/cadastro" element={<Cadastro />} />
          <Route path="/login" element={<Login />} />

          <Route element={<RotaPrivada />}>
            <Route element={<AppLayout />}>
              <Route path="/dashboard" element={<DashboardHome />} />
              <Route path="/disciplinas" element={<DisciplinasPage />} />
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
