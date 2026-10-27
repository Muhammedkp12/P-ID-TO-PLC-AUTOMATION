import { Link } from "react-router-dom";
import HeroSheet from "../components/HeroSheet.jsx";

export default function Home() {
  return (
    <section className="hero">
      <div className="hero-copy">
        <h1>Read every valve, instrument and tag on the sheet.</h1>
        <p>
          Upload a scanned or exported P&amp;ID drawing. Lineweight finds each
          piping and instrumentation symbol, reads the tag next to it, and
          gives you a list you can check, search and export.
        </p>
        <div className="hero-actions">
          <Link className="btn-primary" to="/detect">Upload a drawing</Link>
          <Link className="btn-ghost" to="/how-it-works">See how it works</Link>
        </div>
      </div>
      <div className="hero-visual">
        <HeroSheet />
      </div>
    </section>
  );
}