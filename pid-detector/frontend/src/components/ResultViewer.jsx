import Loader from "./Loader.jsx";

const BRACKET = 14; // length of each corner bracket, in image pixels

function CornerBrackets({ x1, y1, x2, y2, selected }) {
  const cls = `bbox-corner${selected ? " selected" : ""}`;
  const corners = [
    // top-left
    `M${x1},${y1 + BRACKET} L${x1},${y1} L${x1 + BRACKET},${y1}`,
    // top-right
    `M${x2 - BRACKET},${y1} L${x2},${y1} L${x2},${y1 + BRACKET}`,
    // bottom-right
    `M${x2},${y2 - BRACKET} L${x2},${y2} L${x2 - BRACKET},${y2}`,
    // bottom-left
    `M${x1 + BRACKET},${y2} L${x1},${y2} L${x1},${y2 - BRACKET}`,
  ];
  return (
    <>
      {corners.map((d, i) => (
        <path key={i} d={d} className={cls} />
      ))}
    </>
  );
}

export default function ResultViewer({ imageUrl, width, height, detections, selectedIndex, onSelect, isRunning }) {
  const hasResult = imageUrl && width && height;

  return (
    <div className="panel">
      <div className="panel-header">
        <span>02 · Annotated drawing</span>
        {detections?.length > 0 && <span className="count">{detections.length} found</span>}
      </div>

      <div className="viewer-body">
        {isRunning && <Loader label="Scanning tiles, matching symbols…" />}

        {!isRunning && !hasResult && (
          <p className="viewer-empty">Upload a drawing to see detected symbols here.</p>
        )}

        {!isRunning && hasResult && (
          <div className="viewer-canvas-wrap">
            <img src={imageUrl} alt="Uploaded P&ID drawing" />
            <svg
              viewBox={`0 0 ${width} ${height}`}
              preserveAspectRatio="none"
              role="img"
              aria-label="Detected symbol annotations"
            >
              {detections.map((d, i) => {
                const [x1, y1, x2, y2] = d.bbox;
                const selected = i === selectedIndex;
                const label = d.tag ? `${d.class} · ${d.tag}` : d.class;
                const charW = 6.2; // approx mono-font advance at 11px, in SVG units
                const labelW = Math.max(label.length * charW + 10, 30);
                return (
                  <g
                    key={i}
                    onClick={() => onSelect(i)}
                    style={{ cursor: "pointer" }}
                  >
                    <rect
                      x={x1}
                      y={y1}
                      width={x2 - x1}
                      height={y2 - y1}
                      className={`bbox-rect${selected ? " selected" : ""}`}
                    />
                    <CornerBrackets x1={x1} y1={y1} x2={x2} y2={y2} selected={selected} />
                    <rect
                      x={x1}
                      y={Math.max(0, y1 - 16)}
                      width={labelW}
                      height={14}
                      className="bbox-label-bg"
                    />
                    <text
                      x={x1 + 5}
                      y={Math.max(0, y1 - 16) + 10.5}
                      className={`bbox-label-text${selected ? " selected" : ""}`}
                    >
                      {label}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>
        )}
      </div>
    </div>
  );
}
