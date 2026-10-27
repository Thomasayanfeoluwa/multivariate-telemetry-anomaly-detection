import { useMemo } from "react";
import type { GroundTruthWindow } from "../types/api";

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
  retrospectiveWindows?: GroundTruthWindow[];
}

const PAD = { top: 12, right: 12, bottom: 24, left: 64 };

function shortTs(ts: string): string {
  const parts = ts.split(" ");
  return parts.length === 2 ? parts[1] : ts;
}

function toMs(ts: string): number {
  return new Date(ts.replace(" ", "T")).getTime();
}

export function ScoreChart({
  points,
  threshold,
  width = 720,
  height = 240,
  maxPoints = 200,
  retrospectiveWindows,
}: ScoreChartProps) {
  const view = useMemo(() => points.slice(-maxPoints), [points, maxPoints]);

  if (view.length === 0) {
    return (
      <section className="score-chart" aria-label="Anomaly score chart">
        <p className="hint">
          No scored observations in this session yet. Advance past warm-up to
          see scores.
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

  const t0 = toMs(view[0].timestamp);
  const tEnd = toMs(view[view.length - 1].timestamp);
  const xForTs = (ts: string): number => {
    if (tEnd === t0) return PAD.left + innerW / 2;
    const frac = (toMs(ts) - t0) / (tEnd - t0);
    return PAD.left + frac * innerW;
  };

  const visibleWindows = (retrospectiveWindows ?? [])
    .map((w) => {
      const wx1 = Math.max(PAD.left, xForTs(w.start));
      const wx2 = Math.min(width - PAD.right, xForTs(w.end));
      return { ...w, x: wx1, wWidth: wx2 - wx1 };
    })
    .filter((w) => w.wWidth > 0.5);

  const scorePath = view
    .map(
      (p, i) =>
        `${i === 0 ? "M" : "L"} ${xFor(i).toFixed(2)} ${yFor(p.score).toFixed(2)}`,
    )
    .join(" ");

  const thresholdY = yFor(threshold);
  const baselineY = PAD.top + innerH;

  return (
    <section className="score-chart" aria-label="Anomaly score chart">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        width="100%"
        role="img"
        aria-label={`Anomaly score chart for the last ${view.length} scored observations${
          visibleWindows.length > 0
            ? `, with ${visibleWindows.length} retrospective attack window${
                visibleWindows.length === 1 ? "" : "s"
              } overlaid`
            : ""
        }`}
      >
        {visibleWindows.map((w) => (
          <rect
            key={`gt-${w.scenario_id}`}
            x={w.x}
            y={PAD.top}
            width={w.wWidth}
            height={innerH}
            fill="#f59e0b"
            opacity={0.14}
          />
        ))}

        <line
          x1={PAD.left}
          x2={width - PAD.right}
          y1={baselineY}
          y2={baselineY}
          stroke="#3b5875"
          strokeWidth={1}
        />

        <line
          x1={PAD.left}
          x2={width - PAD.right}
          y1={thresholdY}
          y2={thresholdY}
          stroke="#f59e0b"
          strokeWidth={1}
          strokeDasharray="4 4"
        />
        <text
          x={PAD.left - 6}
          y={thresholdY + 4}
          textAnchor="end"
          fontSize={10}
          fill="#f59e0b"
        >
          thr {threshold.toExponential(3)}
        </text>

        {view.length === 1 ? (
          <circle
            cx={xFor(0)}
            cy={yFor(view[0].score)}
            r={3}
            fill="#14b8a6"
          />
        ) : (
          <path d={scorePath} fill="none" stroke="#14b8a6" strokeWidth={1.5} />
        )}

        {view.map((p, i) =>
          p.alert ? (
            <circle
              key={i}
              cx={xFor(i)}
              cy={yFor(p.score)}
              r={2.5}
              fill="#ef4444"
            />
          ) : null,
        )}

        <text x={PAD.left} y={height - 6} fontSize={10} fill="#8ba3ba">
          {shortTs(view[0].timestamp)}
        </text>
        <text
          x={width - PAD.right}
          y={height - 6}
          fontSize={10}
          fill="#8ba3ba"
          textAnchor="end"
        >
          {shortTs(view[view.length - 1].timestamp)}
        </text>
      </svg>
      <p className="chart-caption">
        Last {view.length} scored observation{view.length === 1 ? "" : "s"} ·
        dashed line: threshold · red dots: exceeded threshold
        {visibleWindows.length > 0 && (
          <> · amber bands: known attack windows (retrospective)</>
        )}
      </p>
    </section>
  );
}