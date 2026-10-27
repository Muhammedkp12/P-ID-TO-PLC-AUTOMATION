import { useEffect, useRef, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { checkHealth } from "../api/detectApi.js";
import AuthBackground from "./AuthBackground.jsx";
const ORDER = ["/", "/features", "/how-it-works", "/detect"];

export default function Layout() {
  const [backendReady, setBackendReady] = useState(null);
  const { pathname } = useLocation();

  // Work out which way to slide: forward in the menu order, or back
  const idx = ORDER.indexOf(pathname);
  const last = useRef({ path: pathname, idx, dir: "forward" });
  if (last.current.path !== pathname) {
    last.current = {
      path: pathname,
      idx,
      dir: idx >= last.current.idx ? "forward" : "back",
    };
  }
  const dir = last.current.dir;

  useEffect(() => {
    checkHealth()
      .then((h) => setBackendReady(!!h.model_loaded))
      .catch(() => setBackendReady(false));
  }, []);

  return (
    <div className="app-shell">
      <AuthBackground />
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

      <div className="page-viewport">
        <div key={pathname} className={`page-slide ${dir}`}>
          <Outlet />
        </div>
      </div>

      <footer className="app-footer">
        Lineweight reads P&amp;ID drawings with a YOLO model and Tesseract OCR.
      </footer>
    </div>
  );
}