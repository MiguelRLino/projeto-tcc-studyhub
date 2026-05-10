import { Navigate, Outlet, useLocation } from "react-router-dom";
import { estaAutenticado } from "../services/authService";

export default function RotaPrivada() {
  const location = useLocation();
  if (!estaAutenticado()) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  return <Outlet />;
}
