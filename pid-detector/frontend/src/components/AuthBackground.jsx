export default function AuthBackground() {
  return (
    <svg
      className="wave-bg"
      viewBox="0 0 1440 800"
      preserveAspectRatio="none"
      aria-hidden="true"
    >
      <rect width="1440" height="800" fill="#ffffff" />

      {/* top corner waves */}
      <path
        d="M0,0 H1440 V90 C1200,170 1000,40 760,95 C520,150 300,60 0,140 Z"
        fill="#ffb27a" opacity="0.55"
      />
      <path
        d="M0,0 H1440 V50 C1200,120 1000,10 760,55 C520,100 300,20 0,90 Z"
        fill="#f97316" opacity="0.9"
      />

      {/* bottom waves */}
      <path
        d="M0,620 C240,560 480,700 760,640 C1040,580 1240,520 1440,600 V800 H0 Z"
        fill="#ffcfa8" opacity="0.6"
      />
      <path
        d="M0,690 C260,630 520,760 800,700 C1080,640 1260,620 1440,680 V800 H0 Z"
        fill="#ff9a52" opacity="0.75"
      />
      <path
        d="M0,745 C300,705 560,800 860,752 C1120,708 1300,700 1440,742 V800 H0 Z"
        fill="#f97316"
      />
    </svg>
  );
}