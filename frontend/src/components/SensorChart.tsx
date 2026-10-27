import { useMemo, useState } from "react";

export interface SensorObservation {
  timestamp: string;
  values: Record<string, number>;
}

export interface SensorChartProps {
  observations: SensorObservation[];
  featureNames: string[];
  width?: number;
  height?: number;
  maxPoints?: number;
}

const PAD = { top: 12, right: 12, bottom: 24, left: 64 };

function shortTs(ts: string): string {
  const parts = ts.split(" ");
  return parts.length === 2 ? parts[1] : ts;
}

export function SensorChart({
  observations,
  featureNames,
  width = 720,
  height = 240,
  maxPoints = 200,
}: SensorChartProps) {
  const [feature, setFeature] = useState<string>(featureNames[0] ?? "");

  const view = useMemo(
    () => observations.slice(-maxPoints),
    [observations, maxPoints],
  );

  if (featureNames.length === 0) {
    return (
      <section className="sensor-chart" aria-label="Sensor measurement chart">
        <p className="hint">No feature metadata available.</p>
      </section>
    );
  }

  if (view.length === 0) {
    return (
      <section className="sensor-chart" aria-label="Sensor measurement chart">
        <h2>Sensor measurements</h2>
        <p className="hint">
          No observations accumulated in this session&apos;s history yet.
          Advance the replay to accumulate sensor measurements here. Values
          are shown exactly as recorded in the CSV, without invented units or
          operating limits.
        </p>
      </section>
    );
  }

  const values = view.map((o) => o.values[feature] ?? NaN);
  const finiteVals = values.filter((v) => Number.isFinite(v));
  const vMin = finiteVals.length > 0 ? Math.min(...finiteVals) : 0;
  const vMax = finiteVals.length > 0 ? Math.max(...finiteVals) : 1;
  const pad = (vMax - vMin) * 0.05 || Math.abs(vMax) * 0.01 || 1;
  const yMin = vMin - pad;
  const yMax = vMax + pad;

  const innerW = width - PAD.left - PAD.right;
  const innerH = height - PAD.top - PAD.bottom;

  const xFor = (i: number) => {
    if (view.length <= 1) return PAD.left + innerW / 2;
    return PAD.left + (i / (view.length - 1)) * innerW;
  };
  const yFor = (v: number) => {
    if (!Number.isFinite(v)) return null;
    return PAD.top + innerH - ((v - yMin) / (yMax - yMin)) * innerH;
  };

  const pathParts: string[] = [];
  values.forEach((v, i) => {
    const y = yFor(v);
    if (y === null) return;
    pathParts.push(`${pathParts.length === 0 ? "M" : "L"} ${xFor(i).toFixed(2)} ${y.toFixed(2)}`);
  });
  const path = pathParts.join(" ");

  return (
    <section className="sensor-chart" aria-label="Sensor measurement chart">
      <header className="sensor-header">
        <h2>Sensor measurements</h2>
        <label>
          Feature{" "}
          <select
            value={feature}
            onChange={(e) => setFeature(e.target.value)}
          >
            {featureNames.map((f) => (
              <option key={f} value={f}>
                {f}
              </option>
            ))}
          </select>
        </label>
      </header>

      <svg
        viewBox={`0 0 ${width} ${height}`}
        width="100%"
        role="img"
        aria-label={`${feature} time series over the last ${view.length} observations`}
      >
        <line
          x1={PAD.left}
          x2={width - PAD.right}
          y1={PAD.top + innerH}
          y2={PAD.top + innerH}
          stroke="#888"
          strokeWidth={1}
        />
        {view.length === 1 && yFor(values[0]) !== null ? (
          <circle
            cx={xFor(0)}
            cy={yFor(values[0]) as number}
            r={3}
            fill="#27ae60"
          />
        ) : pathParts.length > 0 ? (
          <path d={path} fill="none" stroke="#27ae60" strokeWidth={1.5} />
        ) : null}

        {/* y-axis labels */}
        <text x={PAD.left - 6} y={PAD.top + 10} fontSize={10} fill="#666" textAnchor="end">
          {yMax.toFixed(3)}
        </text>
        <text
          x={PAD.left - 6}
          y={PAD.top + innerH - 4}
          fontSize={10}
          fill="#666"
          textAnchor="end"
        >
          {yMin.toFixed(3)}
        </text>

        {/* x-axis labels */}
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
        <strong>{feature}</strong> — last {view.length} observation
        {view.length === 1 ? "" : "s"}. Values shown as recorded; no units,
        operating limits, or safety ranges are assumed.
      </p>
    </section>
  );
}