/**
 * Decorative looping animation for the home page.
 *
 * This is NOT real data — it is a stylized illustration of what the
 * dashboard does: a signal that mostly stays low, occasionally spikes
 * above a dashed threshold, and triggers an alert. Loops every 8 seconds.
 *
 * aria-hidden="true" — screen readers skip it.
 * Pure SMIL — no JS state, no animation library, no backend call.
 */
export function AnimatedPreviewChart() {
  return (
    <div className="home-visual" aria-hidden="true">
      <svg
        viewBox="0 0 400 200"
        width="100%"
        preserveAspectRatio="xMidYMid meet"
      >
        {/* Soft gradient fill under the line */}
        <defs>
          <linearGradient id="fill-gradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#14b8a6" stopOpacity="0.35" />
            <stop offset="100%" stopColor="#14b8a6" stopOpacity="0" />
          </linearGradient>
        </defs>

        {/* Baseline grid */}
        <line
          x1="0"
          y1="180"
          x2="400"
          y2="180"
          stroke="#1e3a52"
          strokeWidth="1"
        />

        {/* Threshold (dashed amber) */}
        <line
          x1="0"
          y1="60"
          x2="400"
          y2="60"
          stroke="#f59e0b"
          strokeWidth="1"
          strokeDasharray="4 4"
        />

        {/* Area fill (fades in after the line draws) */}
        <path
          d="M0,180 L20,178 L40,176 L60,178 L80,175 L100,172 L120,168 L140,165 L155,158 L165,140 L172,100 L178,65 L185,52 L192,45 L200,52 L208,75 L215,110 L222,145 L235,160 L260,165 L285,162 L310,158 L335,155 L360,152 L380,148 L400,145 L400,180 Z"
          fill="url(#fill-gradient)"
          opacity="0"
        >
          <animate
            attributeName="opacity"
            values="0;0;0.9;0.9;0"
            dur="8s"
            repeatCount="indefinite"
          />
        </path>

        {/* Signal line (draws itself left-to-right) */}
        <path
          d="M0,180 L20,178 L40,176 L60,178 L80,175 L100,172 L120,168 L140,165 L155,158 L165,140 L172,100 L178,65 L185,52 L192,45 L200,52 L208,75 L215,110 L222,145 L235,160 L260,165 L285,162 L310,158 L335,155 L360,152 L380,148 L400,145"
          fill="none"
          stroke="#14b8a6"
          strokeWidth="2.2"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeDasharray="600"
          strokeDashoffset="600"
        >
          <animate
            attributeName="stroke-dashoffset"
            values="600;0;0;600"
            keyTimes="0;0.75;0.92;1"
            dur="8s"
            repeatCount="indefinite"
          />
        </path>

        {/* Alert dots (fade in when the line crosses threshold) */}
        <circle cx="185" cy="52" r="3.5" fill="#ef4444" opacity="0">
          <animate
            attributeName="opacity"
            values="0;0;0;1;1;0;0"
            keyTimes="0;0.40;0.55;0.62;0.88;0.94;1"
            dur="8s"
            repeatCount="indefinite"
          />
        </circle>
        <circle cx="192" cy="45" r="3.5" fill="#ef4444" opacity="0">
          <animate
            attributeName="opacity"
            values="0;0;0;1;1;0;0"
            keyTimes="0;0.44;0.58;0.64;0.88;0.94;1"
            dur="8s"
            repeatCount="indefinite"
          />
        </circle>
        <circle cx="200" cy="52" r="3.5" fill="#ef4444" opacity="0">
          <animate
            attributeName="opacity"
            values="0;0;0;1;1;0;0"
            keyTimes="0;0.46;0.60;0.66;0.88;0.94;1"
            dur="8s"
            repeatCount="indefinite"
          />
        </circle>
      </svg>

      <p className="home-visual-caption">
        Signal · threshold · alerts
      </p>
    </div>
  );
}