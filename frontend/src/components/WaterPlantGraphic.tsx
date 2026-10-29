export function WaterPlantGraphic() {
  return (
    <div className="plant-graphic-container">
      <svg viewBox="0 0 600 200" className="plant-graphic" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <filter id="glow-heavy" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="6" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
          <linearGradient id="tank-left" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#0d9488" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#0a1929" stopOpacity="0.8" />
          </linearGradient>
          <linearGradient id="tank-right" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#14b8a6" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#0a1929" stopOpacity="0.9" />
          </linearGradient>
          <linearGradient id="tank-top" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#2dd4bf" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#0f766e" stopOpacity="0.4" />
          </linearGradient>
        </defs>

        {/* Background Grid / Starfield */}
        <g opacity="0.15" stroke="var(--accent)" strokeWidth="1">
          <line x1="100" y1="150" x2="500" y2="150" />
          <line x1="100" y1="170" x2="500" y2="170" />
          <line x1="150" y1="130" x2="150" y2="190" />
          <line x1="250" y1="130" x2="250" y2="190" />
          <line x1="350" y1="130" x2="350" y2="190" />
          <line x1="450" y1="130" x2="450" y2="190" />
        </g>

        {/* Pipes */}
        <g fill="none" stroke="var(--accent)" strokeWidth="2" opacity="0.6">
          <path d="M 180 120 L 180 80 L 300 80" />
          <path d="M 300 110 L 300 60 L 420 60" />
          <path d="M 420 130 L 420 90 L 480 90" />
          <path d="M 250 140 L 250 100 L 300 100" />
        </g>

        {/* Left Tanks (Stage 1) */}
        <g transform="translate(140, 80)">
          {/* Tank 1 */}
          <polygon points="0,20 40,0 80,20 40,40" fill="url(#tank-top)" filter="url(#glow-heavy)" />
          <polygon points="0,20 40,40 40,70 0,50" fill="url(#tank-left)" />
          <polygon points="40,40 80,20 80,50 40,70" fill="url(#tank-right)" />
          {/* Tank 2 */}
          <polygon points="60,30 100,10 140,30 100,50" fill="url(#tank-top)" />
          <polygon points="60,30 100,50 100,80 60,60" fill="url(#tank-left)" />
          <polygon points="100,50 140,30 140,60 100,80" fill="url(#tank-right)" />
        </g>

        {/* Center Tower (Stage 2) */}
        <g transform="translate(280, 40)">
          {/* Tower Body */}
          <polygon points="0,40 20,20 40,40 20,60" fill="url(#tank-top)" filter="url(#glow-heavy)" />
          <polygon points="0,40 20,60 20,100 0,80" fill="url(#tank-left)" />
          <polygon points="20,60 40,40 40,80 20,100" fill="url(#tank-right)" />
          {/* Tower Top dome */}
          <ellipse cx="20" cy="20" rx="20" ry="10" fill="url(#tank-top)" stroke="var(--accent)" strokeWidth="1" />
        </g>

        {/* Right Tanks (Stage 3) */}
        <g transform="translate(400, 70)">
          {/* Circular Tank 1 */}
          <ellipse cx="30" cy="20" rx="30" ry="15" fill="url(#tank-top)" filter="url(#glow-heavy)" />
          <path d="M 0 20 L 0 60 A 30 15 0 0 0 60 60 L 60 20" fill="url(#tank-right)" />
          
          {/* Circular Tank 2 */}
          <ellipse cx="80" cy="40" rx="20" ry="10" fill="url(#tank-top)" />
          <path d="M 60 40 L 60 70 A 20 10 0 0 0 100 70 L 100 40" fill="url(#tank-left)" />
        </g>

        {/* Glowing Nodes (Valves/Sensors) */}
        <circle cx="180" cy="80" r="4" fill="var(--accent)" filter="url(#glow-heavy)" />
        <circle cx="300" cy="80" r="4" fill="var(--accent)" filter="url(#glow-heavy)" />
        <circle cx="300" cy="60" r="4" fill="var(--accent)" filter="url(#glow-heavy)" />
        <circle cx="420" cy="60" r="4" fill="var(--accent)" filter="url(#glow-heavy)" />
      </svg>
    </div>
  );
}