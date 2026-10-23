export default function Features() {
  return (
    <section className="section">
      <div className="features">
        <div className="features-intro">
          <h2>From a flat drawing to structured data</h2>
          <p>
            P&amp;ID sheets hold hundreds of symbols and tags. Lineweight turns
            them into rows you can work with.
          </p>
        </div>
        <div className="feature-list">
          <div className="feature">
            <h3>Find symbols</h3>
            <p>A YOLO model locates valves, instruments and equipment and draws a box around each one.</p>
          </div>
          <div className="feature">
            <h3>Read tags</h3>
            <p>OCR reads the text next to each symbol, so you get tags like 27-MOV-021 instead of just a shape.</p>
          </div>
          <div className="feature">
            <h3>See confidence</h3>
            <p>Every detection shows how sure the model is, so weak results are easy to spot and recheck.</p>
          </div>
          <div className="feature">
            <h3>Review on the drawing</h3>
            <p>Click a row to highlight its symbol on the sheet, or click a box to jump to its row.</p>
          </div>
        </div>
      </div>
    </section>
  );
}