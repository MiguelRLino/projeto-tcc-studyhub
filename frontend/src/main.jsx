import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { GoogleOAuthProvider } from "@react-oauth/google";
import "./index.css";
import "./styles/shell.css";
import "./styles/tema.css";
import { aplicarTemaSalvo } from "./utils/tema";
import App from "./App.jsx";

aplicarTemaSalvo();

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || "";

const app = (
  <StrictMode>
    {googleClientId ? (
      <GoogleOAuthProvider clientId={googleClientId}>
        <App />
      </GoogleOAuthProvider>
    ) : (
      <App />
    )}
  </StrictMode>
);

createRoot(document.getElementById("root")).render(app);
