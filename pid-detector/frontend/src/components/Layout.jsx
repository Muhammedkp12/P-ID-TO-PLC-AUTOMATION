import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { checkHealth } from "../api/detectApi.js";

export default function Layout() {
  const [backendReady, setBackendReady] = useState(null);

  useEffect(() => {
    checkHealth()
      .then((h) => setBackendReady(!!h.model_loaded))
      .catch(() => setBackendReady(false));
  }, []);

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <span className="brand-mark">Lineweight</span>
          <span className="brand-tag">P&amp;ID symbol detection</span>
        </div>

        <nav className="nav-links" aria-label="Pages">
          <NavLink to="/" end>Home</NavLink>
          <NavLink to="/features">Features</NavLink>
          <NavLink to="/how-it-works">How it works</NavLink>
          <NavLink to="/detect">Try it</NavLink>
        </nav>

        <div className="header-status">
          <span className={`status-dot ${backendReady ? "ready" : ""}`} />
          {backendReady === null
            ? "Checking backend…"
            : backendReady
            ? "Model loaded"
            : "Model unavailable"}
        </div>
      </header>

      <Outlet />

      <footer className="app-footer">
        Lineweight reads P&amp;ID drawings with a YOLO model and Tesseract OCR.
      </footer>
    </div>
  );
}