import type { FC } from "react";

export interface FeatureAttributionProps {
  residuals: Record<string, number> | null;
  score: number | null;
  threshold: number;
  timestamp: string | null;
  width?: number;
  topN?: number;
}

const PAD = { top: 12, right: 60, bottom: 20, left: 88 };
const BAR_HEIGHT = 16;
const BAR_GAP = 6;

const FeatureAttribution: FC<FeatureAttributionProps> = ({
  residuals,
  score,
  threshold,
  timestamp,
  width = 720,
  topN = 8,
}) => {
  if (residuals === null) {
    return (
      <section className="feature-attribution" aria-label="Feature attribution">
        <h2>Feature attribution</h2>
        <p className="hint">
          Appears after the first threshold crossing. Shows which sensors
          contributed most to the model&apos;s reconstruction error for that
          alert.
        </p>
      </section>
    );
  }

  const isAlert = score !== null && score > threshold;
  const sorted = Object.entries(residuals)
    .sort(([, a], [, b]) => b - a)
    .slice(0, topN);
  const maxVal = sorted.length > 0 ? sorted[0][1] : 1;
  const total = Object.values(residuals).reduce((a, b) => a + b, 0);

  const height = PAD.top + PAD.bottom + topN * (BAR_HEIGHT + BAR_GAP);
  const innerW = width - PAD.left - PAD.right;

  return (
    <section className="feature-attribution" aria-label="Feature attribution">
      <h2>Feature attribution</h2>
      {!isAlert && timestamp !== null && (
        <p className="attribution-note">
          Last observation at {timestamp} — below threshold. Attribution shown
          for reference.
        </p>
      )}
      {isAlert && timestamp !== null && (
        <p className="attribution-note attribution-alert">
          Alert at {timestamp} — top contributing sensors:
        </p>
      )}

      <svg
        viewBox={`0 0 ${width} ${height}`}
        width="100%"
        role="img"
        aria-label={`Top ${topN} sensors by reconstruction error`}
      >
        {sorted.map(([name, val], i) => {
          const y = PAD.top + i * (BAR_HEIGHT + BAR_GAP);
          const barW = (val / maxVal) * innerW;
          const pct = total > 0 ? (val / total) * 100 : 0;
          return (
            <g key={name}>
              <text
                x={PAD.left - 8}
                y={y + BAR_HEIGHT * 0.75}
                fontSize={11}
                fill="#8ba3ba"
                textAnchor="end"
                fontFamily="var(--mono)"
              >
                {name}
              </text>
              <rect
                x={PAD.left}
                y={y}
                width={barW}
                height={BAR_HEIGHT}
                fill={isAlert ? "#ef4444" : "#14b8a6"}
                opacity={0.85}
                rx={2}
              />
              <text
                x={PAD.left + barW + 6}
                y={y + BAR_HEIGHT * 0.75}
                fontSize={10}
                fill="#8ba3ba"
                fontFamily="var(--mono)"
              >
                {pct.toFixed(1)}%
              </text>
            </g>
          );
        })}
      </svg>
      <p className="chart-caption">
        Percentages show each sensor&apos;s share of total reconstruction error.
        Higher = model had more difficulty reconstructing that signal.
      </p>
    </section>
  );
};

export { FeatureAttribution };