import { AnimatedPreviewChart } from "../components/AnimatedPreviewChart";

const REPO_URL =
  (import.meta.env.VITE_REPO_URL as string | undefined) ??
  "https://github.com/";

export interface HomeProps {
  onEnter: () => void;
}

export function Home({ onEnter }: HomeProps) {
  return (
    <div className="home">
      <div className="home-hero">
        <div className="home-hero-text">
          <div className="home-eyebrow">Industrial Anomaly Detection</div>
          <h1 className="home-title">SWaT Process Anomaly Monitor</h1>
          <p className="home-description">
            Historical replay of recorded water-treatment measurements
            through a frozen TCN autoencoder. Explore anomaly scores,
            threshold crossings, and retrospective benchmark results in real
            time.
          </p>
          <button type="button" className="home-cta" onClick={onEnter}>
            Open dashboard →
          </button>
        </div>
        <AnimatedPreviewChart />
      </div>
      <footer className="home-footer">
        <p className="home-disclaimer">
          This is a research prototype. Model alerts are advisory outputs
          requiring human review — not confirmed attacks, equipment failures,
          or safety events.
        </p>
        <a
          className="home-repo-link"
          href={REPO_URL}
          target="_blank"
          rel="noopener noreferrer"
        >
          View source on GitHub
        </a>
      </footer>
    </div>
  );
}