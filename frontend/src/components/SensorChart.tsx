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

const MAX_SELECTED = 4;
const LINE_COLORS = ["#14b8a6", "#f59e0b", "#a78bfa", "#ef4444"];
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
  const [selected, setSelected] = useState<string[]>(() =>
    featureNames.length > 0 ? [featureNames[0]] : [],
  );

  const view = useMemo(
    () => observations.slice(-maxPoints),
    [observations, maxPoints],
  );

  const toggle = (name: string) => {
    setSelected((prev) => {
      if (prev.includes(name)) {
        if (prev.length === 1) return prev;
        return prev.filter((f) => f !== name);
      }
      if (prev.length >= MAX_SELECTED) return prev;
      return [...prev, name];
    });
  };

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
          No observations in this session yet. Advance the replay to see
          measurements.
        </p>
      </section>
    );
  }

  const multiMode = selected.length > 1;

  const featureRanges: Record<string, { min: number; max: number }> = {};
  for (const feat of selected) {
    const vals = view
      .map((o) => o.values[feat] ?? NaN)
      .filter(Number.isFinite);
    if (vals.length === 0) {
      featureRanges[feat] = { min: 0, max: 1 };
    } else {
      const min = Math.min(...vals);
      const max = Math.max(...vals);
      featureRanges[feat] = { min, max: max === min ? min + 1 : max };
    }
  }

  const innerW = width - PAD.left - PAD.right;
  const innerH = height - PAD.top - PAD.bottom;

  const xFor = (i: number) => {
    if (view.length <= 1) return PAD.left + innerW / 2;
    return PAD.left + (i / (view.length - 1)) * innerW;
  };

  const yForNorm = (v: number) => PAD.top + innerH - v * innerH;
  const singleRange = multiMode ? null : featureRanges[selected[0]];
  const yForRaw = (v: number) => {
    if (!singleRange) return PAD.top + innerH;
    const { min, max } = singleRange;
    return PAD.top + innerH - ((v - min) / (max - min)) * innerH;
  };

  const makePath = (feat: string) => {
    const parts: string[] = [];
    view.forEach((o, i) => {
      const v = o.values[feat];
      if (!Number.isFinite(v)) return;
      let y: number;
      if (multiMode) {
        const { min, max } = featureRanges[feat];
        y = yForNorm((v - min) / (max - min));
      } else {
        y = yForRaw(v);
      }
      parts.push(
        `${parts.length === 0 ? "M" : "L"} ${xFor(i).toFixed(2)} ${y.toFixed(2)}`,
      );
    });
    return parts.join(" ");
  };

  return (
    <section className="sensor-chart" aria-label="Sensor measurement chart">
      <header className="sensor-header">
        <h2>Sensor measurements</h2>
        <details className="sensor-picker">
          <summary>
            {selected.length} of {MAX_SELECTED} selected
          </summary>
          <div className="sensor-feature-list">
            {featureNames.map((f) => (
              <label key={f} className="feature-checkbox">
                <input
                  type="checkbox"
                  checked={selected.includes(f)}
                  onChange={() => toggle(f)}
                  disabled={
                    !selected.includes(f) && selected.length >= MAX_SELECTED
                  }
                />
                {f}
              </label>
            ))}
          </div>
        </details>
      </header>

      <svg
        viewBox={`0 0 ${width} ${height}`}
        width="100%"
        role="img"
        aria-label={`${selected.join(", ")} time series over the last ${view.length} observations`}
      >
        <line
          x1={PAD.left}
          x2={width - PAD.right}
          y1={PAD.top + innerH}
          y2={PAD.top + innerH}
          stroke="#3b5875"
          strokeWidth={1}
        />

        {selected.map((feat, idx) => {
          const color = LINE_COLORS[idx] ?? "#14b8a6";
          if (view.length === 1 && Number.isFinite(view[0].values[feat])) {
            const v = view[0].values[feat];
            const y = multiMode
              ? yForNorm(
                  (v - featureRanges[feat].min) /
                    (featureRanges[feat].max - featureRanges[feat].min),
                )
              : yForRaw(v);
            return <circle key={feat} cx={xFor(0)} cy={y} r={3} fill={color} />;
          }
          return (
            <path
              key={feat}
              d={makePath(feat)}
              fill="none"
              stroke={color}
              strokeWidth={1.5}
            />
          );
        })}

        {!multiMode && singleRange && (
          <>
            <text
              x={PAD.left - 6}
              y={PAD.top + 10}
              fontSize={10}
              fill="#8ba3ba"
              textAnchor="end"
            >
              {singleRange.max.toFixed(3)}
            </text>
            <text
              x={PAD.left - 6}
              y={PAD.top + innerH - 4}
              fontSize={10}
              fill="#8ba3ba"
              textAnchor="end"
            >
              {singleRange.min.toFixed(3)}
            </text>
          </>
        )}

        {multiMode && (
          <>
            <text
              x={PAD.left - 6}
              y={PAD.top + 10}
              fontSize={10}
              fill="#8ba3ba"
              textAnchor="end"
            >
              100%
            </text>
            <text
              x={PAD.left - 6}
              y={PAD.top + innerH - 4}
              fontSize={10}
              fill="#8ba3ba"
              textAnchor="end"
            >
              0%
            </text>
          </>
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

      <div className="sensor-legend">
        {selected.map((feat, idx) => (
          <span key={feat} className="sensor-legend-item">
            <span
              className="sensor-legend-swatch"
              style={{ background: LINE_COLORS[idx] ?? "#14b8a6" }}
            />
            {feat}
          </span>
        ))}
      </div>

      <p className="chart-caption">
        {multiMode
          ? `Last ${view.length} observations · each feature normalized to its own 0–100% range`
          : `${selected[0]} — last ${view.length} observations`}
      </p>
    </section>
  );
}