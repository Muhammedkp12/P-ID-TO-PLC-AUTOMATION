import { Link } from "react-router-dom";

export default function HowItWorks() {
  return (
    <section className="band">
      <div className="band-inner">
        <h2>How it works</h2>
        <ol className="steps">
          <li>
            <span className="step-num">1</span>
            <h3>Upload a sheet</h3>
            <p>Drop in a JPEG, PNG, WEBP or TIFF of your P&amp;ID.</p>
          </li>
          <li>
            <span className="step-num">2</span>
            <h3>Run detection</h3>
            <p>The model scans the drawing and finds the symbols, then OCR reads each tag.</p>
          </li>
          <li>
            <span className="step-num">3</span>
            <h3>Review the results</h3>
            <p>Check the boxes on the drawing and the detection list side by side.</p>
          </li>
        </ol>
        <p style={{ marginTop: 24 }}>
          <Link className="btn-primary" to="/detect">Try it now</Link>
        </p>
      </div>
    </section>
  );
}