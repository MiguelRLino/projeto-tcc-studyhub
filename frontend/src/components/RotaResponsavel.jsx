import { Navigate, Outlet, useLocation } from "react-router-dom";
import { ehResponsavel, estaAutenticado } from "../services/authService";

export default function RotaResponsavel() {
  const location = useLocation();
  if (!estaAutenticado()) {
    return (
      <Navigate to="/login" replace state={{ from: location.pathname }} />
    );
  }
  if (!ehResponsavel()) {
    return <Navigate to="/dashboard" replace />;
  }
  return <Outlet />;
}
