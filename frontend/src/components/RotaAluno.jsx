import { Navigate, Outlet } from "react-router-dom";
import { ehAluno, estaAutenticado } from "../services/authService";

export default function RotaAluno() {
  if (!estaAutenticado()) {
    return <Navigate to="/login" replace />;
  }
  if (!ehAluno()) {
    return <Navigate to="/responsavel" replace />;
  }
  return <Outlet />;
}
