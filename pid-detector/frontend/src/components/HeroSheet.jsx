export default function HeroSheet() {
  return (
    <div className="sheet" aria-hidden="true">
      <svg viewBox="0 0 440 260" role="img">
        <line x1="0" y1="180" x2="440" y2="180" className="pipe" />
        <polygon points="70,166 90,180 70,194" className="sym" />
        <polygon points="110,166 90,180 110,194" className="sym" />
        <line x1="90" y1="180" x2="90" y2="160" className="sym" />
        <line x1="82" y1="160" x2="98" y2="160" className="sym" />
        <polygon points="250,166 270,180 250,194" className="sym" />
        <polygon points="290,166 270,180 290,194" className="sym" />
        <line x1="270" y1="180" x2="270" y2="150" className="sym" />
        <path d="M254,150 A16,16 0 0 1 286,150 Z" className="sym" />
        <circle cx="360" cy="90" r="16" className="sym" />
        <text x="360" y="94" textAnchor="middle" className="sym-text">FT</text>
        <line x1="360" y1="106" x2="360" y2="180" className="sym dashed" />

        <rect x="60" y="150" width="60" height="60" rx="2" pathLength="1" className="hero-box" style={{ animationDelay: "0.3s" }} />
        <rect x="60" y="212" width="156" height="18" className="hero-label" />
        <text x="66" y="225" className="hero-label-text">gate valve · 27-MOV-021</text>

        <rect x="240" y="126" width="60" height="84" rx="2" pathLength="1" className="hero-box" style={{ animationDelay: "0.8s" }} />
        <rect x="240" y="212" width="150" height="18" className="hero-label" />
        <text x="246" y="225" className="hero-label-text">control valve · FV-310</text>

        <rect x="336" y="66" width="48" height="48" rx="2" pathLength="1" className="hero-box" style={{ animationDelay: "1.3s" }} />
        <rect x="248" y="46" width="136" height="18" className="hero-label" />
        <text x="254" y="59" className="hero-label-text">transmitter · FT-104</text>
      </svg>
    </div>
  );
}