import { useMemo } from "react";

export interface ScorePoint {
  timestamp: string;
  score: number;
  alert: boolean;
}

export interface ScoreChartProps {
  points: ScorePoint[];
  threshold: number;
  width?: number;
  height?: number;
  maxPoints?: number;
}

const PAD = { top: 12, right: 12, bottom: 24, left: 64 };

function shortTs(ts: string): string {
  // "2016-01-01 02:23:47" -> "02:23:47"; leave as-is otherwise.
  const parts = ts.split(" ");
  return parts.length === 2 ? parts[1] : ts;
}

export function ScoreChart({
  points,
  threshold,
  width = 720,
  height = 240,
  maxPoints = 200,
}: ScoreChartProps) {
  const view = useMemo(() => points.slice(-maxPoints), [points, maxPoints]);

  if (view.length === 0) {
    return (
      <section className="score-chart" aria-label="Anomaly score chart">
        <p className="hint">
          No scored observations yet. Advance the replay past warm-up to see
          scores here. Warm-up is the first 29 observations; no score is
          produced during warm-up, and the absence of a score does not
          indicate normal behaviour.
        </p>
      </section>
    );
  }

  const innerW = width - PAD.left - PAD.right;
  const innerH = height - PAD.top - PAD.bottom;

  const peak = view.reduce((m, p) => (p.score > m ? p.score : m), 0);
  const yMax = Math.max(threshold * 1.2, peak * 1.1, 1e-6);

  const xFor = (i: number) => {
    if (view.length <= 1) return PAD.left + innerW / 2;
    return PAD.left + (i / (view.length - 1)) * innerW;
  };
  const yFor = (v: number) => PAD.top + innerH - (v / yMax) * innerH;

  const scorePath = view
    .map((p, i) => `${i === 0 ? "M" : "L"} ${xFor(i).toFixed(2)} ${yFor(p.score).toFixed(2)}`)
    .join(" ");

  const thresholdY = yFor(threshold);
  const baselineY = PAD.top + innerH;

  return (
    <section className="score-chart" aria-label="Anomaly score chart">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        width="100%"
        role="img"
        aria-label={`Anomaly score chart for the last ${view.length} scored observations`}
      >
        {/* y-axis baseline */}
        <line
          x1={PAD.left}
          x2={width - PAD.right}
          y1={baselineY}
          y2={baselineY}
          stroke="#888"
          strokeWidth={1}
        />

        {/* frozen threshold line */}
        <line
          x1={PAD.left}
          x2={width - PAD.right}
          y1={thresholdY}
          y2={thresholdY}
          stroke="#c0392b"
          strokeWidth={1}
          strokeDasharray="4 4"
        />
        <text
          x={PAD.left - 6}
          y={thresholdY + 4}
          textAnchor="end"
          fontSize={10}
          fill="#c0392b"
        >
          thr {threshold.toExponential(3)}
        </text>

        {/* score series */}
        {view.length === 1 ? (
          <circle cx={xFor(0)} cy={yFor(view[0].score)} r={3} fill="#2980b9" />
        ) : (
          <path d={scorePath} fill="none" stroke="#2980b9" strokeWidth={1.5} />
        )}

        {/* alert points */}
        {view.map((p, i) =>
          p.alert ? (
            <circle
              key={i}
              cx={xFor(i)}
              cy={yFor(p.score)}
              r={2.5}
              fill="#c0392b"
            />
          ) : null,
        )}

        {/* x-axis labels (time-only for readability) */}
        <text x={PAD.left} y={height - 6} fontSize={10} fill="#666">
          {shortTs(view[0].timestamp)}
        </text>
        <text
          x={width - PAD.right}
          y={height - 6}
          fontSize={10}
          fill="#666"
          textAnchor="end"
        >
          {shortTs(view[view.length - 1].timestamp)}
        </text>
      </svg>
      <p className="chart-caption">
        Last {view.length} scored observation{view.length === 1 ? "" : "s"}.
        Dashed line: frozen threshold. Red dots: scores exceeded the threshold.
        Alerts are advisory; they are not confirmed attacks or failures.
      </p>
    </section>
  );
}