import type { ScorePoint } from "./ScoreChart";

export interface SessionSummaryProps {
  points: ScorePoint[];
  threshold: number;
}

const EPISODE_GAP_SEC = 1.5;

interface Episode {
  startTs: string;
  endTs: string;
  count: number;
  peak: number;
  peakTs: string;
}

function toMs(ts: string): number {
  return new Date(ts.replace(" ", "T")).getTime();
}

function computeEpisodes(points: ScorePoint[]): Episode[] {
  const episodes: Episode[] = [];
  let current: Episode | null = null;
  let lastAlertMs = 0;

  for (const p of points) {
    if (!p.alert) continue;
    const ms = toMs(p.timestamp);
    const startsNew =
      current === null || ms - lastAlertMs > EPISODE_GAP_SEC * 1000;

    if (startsNew) {
      if (current !== null) episodes.push(current);
      current = {
        startTs: p.timestamp,
        endTs: p.timestamp,
        count: 1,
        peak: p.score,
        peakTs: p.timestamp,
      };
    } else if (current !== null) {
      current.endTs = p.timestamp;
      current.count += 1;
      if (p.score > current.peak) {
        current.peak = p.score;
        current.peakTs = p.timestamp;
      }
    }
    lastAlertMs = ms;
  }
  if (current !== null) episodes.push(current);
  return episodes;
}

function formatDuration(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) return "—";
  if (seconds < 60) return `${Math.round(seconds)} s`;
  const m = Math.floor(seconds / 60);
  const s = Math.round(seconds - m * 60);
  if (m < 60) return s === 0 ? `${m} min` : `${m} min ${s} s`;
  const h = Math.floor(m / 60);
  const mm = m - h * 60;
  return mm === 0 ? `${h} h` : `${h} h ${mm} min`;
}

export function SessionSummary({ points, threshold }: SessionSummaryProps) {
  if (points.length === 0 || threshold <= 0) {
    return null;
  }

  const scored = points.length;
  const alerts = points.filter((p) => p.alert).length;
  const episodes = computeEpisodes(points);

  const peakPoint = points.reduce(
    (m, p) => (p.score > m.score ? p : m),
    points[0],
  );

  const firstTs = points[0].timestamp;
  const lastTs = points[points.length - 1].timestamp;
  const peakMultiplier = peakPoint.score / threshold;
  const alertCoveragePct = scored > 0 ? (alerts / scored) * 100 : 0;

  const longestEpisode =
    episodes.length === 0
      ? null
      : episodes.reduce((m, e) => (e.count > m.count ? e : m), episodes[0]);

  const intro =
    alerts === 0
      ? `This replay reviewed ${scored.toLocaleString()} observations recorded between ${firstTs} and ${lastTs}. The model's anomaly score stayed below threshold throughout this window.`
      : `This replay reviewed ${scored.toLocaleString()} observations recorded between ${firstTs} and ${lastTs}. The model flagged ${episodes.length.toLocaleString()} anomalous ${
          episodes.length === 1 ? "period" : "periods"
        }, covering ${alerts.toLocaleString()} observations.`;

  const detail: string[] = [];
  if (episodes.length > 0) {
    detail.push(
      `The strongest alert reached ${peakMultiplier.toFixed(1)}× threshold at ${peakPoint.timestamp}.`,
    );
    if (longestEpisode !== null) {
      const longestSec =
        (toMs(longestEpisode.endTs) - toMs(longestEpisode.startTs)) / 1000;
      detail.push(
        `The longest continuous period lasted ${formatDuration(longestSec)}.`,
      );
    }
  }

  return (
    <section className="session-summary" aria-label="Session summary">
      <h2>Session summary</h2>
      <p className="summary-intro">{intro}</p>
      {detail.length > 0 && (
        <p className="summary-detail">{detail.join(" ")}</p>
      )}

      <div className="summary-stats">
        <div className="summary-stat">
          <div className="summary-stat-value">
            {alerts.toLocaleString()}
          </div>
          <div className="summary-stat-label">Alert observations</div>
        </div>
        <div className="summary-stat">
          <div className="summary-stat-value">
            {episodes.length.toLocaleString()}
          </div>
          <div className="summary-stat-label">
            Anomalous {episodes.length === 1 ? "period" : "periods"}
          </div>
        </div>
        <div className="summary-stat summary-stat-attention">
          <div className="summary-stat-value">
            {peakMultiplier.toFixed(1)}×
          </div>
          <div className="summary-stat-label">Peak vs threshold</div>
        </div>
        <div className="summary-stat">
          <div className="summary-stat-value">
            {alertCoveragePct.toFixed(1)}%
          </div>
          <div className="summary-stat-label">Time above threshold</div>
        </div>
      </div>

      <p className="summary-spacer-note">
        Duration shown is the recorded interval between first and last
        observations, not continuous sampling time.
      </p>
    </section>
  );
}