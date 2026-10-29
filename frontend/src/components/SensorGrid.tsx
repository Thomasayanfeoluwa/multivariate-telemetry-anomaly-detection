import { useState } from "react";
import { Sparkline } from "./Sparkline";

export interface SensorObservation {
  timestamp: string;
  values: Record<string, number>;
}

export interface SensorGridProps {
  observations: SensorObservation[];
  featureNames: string[];
}

export function SensorGrid({ observations, featureNames }: SensorGridProps) {
  // Default to showing the first 6 sensors
  const [selected, setSelected] = useState<string[]>(
    featureNames.slice(0, 6)
  );

  const toggleSensor = (name: string) => {
    setSelected((prev) => {
      if (prev.includes(name)) {
        // Don't allow removing the last one
        if (prev.length === 1) return prev;
        return prev.filter((f) => f !== name);
      }
      return [...prev, name];
    });
  };

  if (observations.length === 0) {
    return (
      <section className="sensor-grid-section">
        <h2>Sensor Grid Monitoring</h2>
        <p className="hint">
          No observations yet. Advance the replay to see real-time sensor values.
        </p>
      </section>
    );
  }

  // Get the last 20 observations for the sparklines
  const recentObs = observations.slice(-20);
  const latestObs = observations[observations.length - 1];

  return (
    <section className="sensor-grid-section">
      <header className="sensor-grid-header">
        <h2>Sensor Grid Monitoring</h2>
        
        {/* Sensor Selection Dropdown */}
        <details className="sensor-picker">
          <summary>Select Sensors ({selected.length})</summary>
          <div className="sensor-feature-list">
            {featureNames.map((f) => (
              <label key={f} className="feature-checkbox">
                <input
                  type="checkbox"
                  checked={selected.includes(f)}
                  onChange={() => toggleSensor(f)}
                />
                {f}
              </label>
            ))}
          </div>
        </details>
      </header>

      <div className="sensor-grid">
        {selected.map((feat) => {
          const series = recentObs
            .map((o) => o.values[feat])
            .filter((v) => Number.isFinite(v));
          
          const currentVal = latestObs.values[feat];

          return (
            <div key={feat} className="sensor-card">
              <div className="sensor-card-header">
                <span className="sensor-name">{feat}</span>
                <span className="sensor-value">
                  {currentVal !== undefined ? currentVal.toFixed(3) : "—"}
                </span>
              </div>
              <div className="sensor-sparkline">
                <Sparkline data={series} color="var(--accent)" />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}