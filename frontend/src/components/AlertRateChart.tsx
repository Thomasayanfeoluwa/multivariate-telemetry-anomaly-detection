import { useMemo } from "react";
import type { ScorePoint } from "./ScoreChart";

export interface AlertRateChartProps {
  points: ScorePoint[];
  width?: number;
  height?: number;
}

const PAD = { top: 16, right: 16, bottom: 32, left: 56 };

interface Bucket {
  label: string;
  alerts: number;
  total: number;
}

function bucketByMinute(points: ScorePoint[]): Bucket[] {
  const map = new Map<string, { alerts: number; total: number }>();
  for (const p of points) {
    const minute = p.timestamp.slice(11, 16);
    const b = map.get(minute) ?? { alerts: 0, total: 0 };
    b.total += 1;
    if (p.alert) b.alerts += 1;
    map.set(minute, b);
  }
  return Array.from(map.entries()).map(([label, b]) => ({
    label,
    alerts: b.alerts,
    total: b.total,
  }));
}

export function AlertRateChart({
  points,
  width = 720,
  height = 200,
}: AlertRateChartProps) {
  const buckets = useMemo(() => bucketByMinute(points), [points]);
  const totalAlerts = buckets.reduce((a, b) => a + b.alerts, 0);

  if (points.length === 0) {
    return (
      <section className="alert-rate" aria-label="Alert rate over time">
        <h2>Alert rate over time</h2>
        <p className="hint">
          No observations in this session yet. Advance the replay to see alert
          distribution across time.
        </p>
      </section>
    );
  }

  if (totalAlerts === 0) {
    return (
      <section className="alert-rate" aria-label="Alert rate over time">
        <h2>Alert rate over time</h2>
        <p className="hint">
          No threshold crossings in this session yet. Once alerts fire, their
          distribution across time appears here.
        </p>
      </section>
    );
  }

  const innerW = width - PAD.left - PAD.right;
  const innerH = height - PAD.top - PAD.bottom;
  const maxAlerts = buckets.reduce((m, b) => Math.max(m, b.alerts), 1);
  const barW = innerW / buckets.length;

  return (
    <section className="alert-rate" aria-label="Alert rate over time">
      <h2>Alert rate over time</h2>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        width="100%"
        role="img"
        aria-label={`Alert count per minute across ${buckets.length} minutes, max ${maxAlerts} per minute`}
      >
        {buckets.map((b, i) => {
          const x = PAD.left + i * barW;
          const barH = (b.alerts / maxAlerts) * innerH;
          return (
            <rect
              key={b.label}
              x={x + 1}
              y={PAD.top + innerH - barH}
              width={Math.max(1, barW - 2)}
              height={barH}
              fill="#ef4444"
              opacity={0.8}
            />
          );
        })}
        <line
          x1={PAD.left}
          x2={width - PAD.right}
          y1={PAD.top + innerH}
          y2={PAD.top + innerH}
          stroke="#3b5875"
          strokeWidth={1}
        />
        <text
          x={PAD.left - 6}
          y={PAD.top + 6}
          fontSize={10}
          fill="#8ba3ba"
          textAnchor="end"
        >
          {maxAlerts}
        </text>
        <text
          x={PAD.left - 6}
          y={PAD.top + innerH}
          fontSize={10}
          fill="#8ba3ba"
          textAnchor="end"
        >
          0
        </text>
        {buckets.length > 1 && (
          <>
            <text x={PAD.left} y={height - 6} fontSize={10} fill="#8ba3ba">
              {buckets[0].label}
            </text>
            <text
              x={width - PAD.right}
              y={height - 6}
              fontSize={10}
              fill="#8ba3ba"
              textAnchor="end"
            >
              {buckets[buckets.length - 1].label}
            </text>
          </>
        )}
      </svg>
      <p className="chart-caption">
        Alerts per minute across {buckets.length} minute
        {buckets.length === 1 ? "" : "s"} · total {totalAlerts.toLocaleString()}{" "}
        alert{totalAlerts === 1 ? "" : "s"}
      </p>
    </section>
  );
}