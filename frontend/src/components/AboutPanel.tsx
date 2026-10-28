export function AboutPanel() {
    return (
        <section className="about-panel" aria-label="About this project">
            <div className="about-grid">
                <div className="about-column">
                    <h3>Purpose</h3>
                    <p>
                        Learn the normal behaviour of a six-stage water-treatment process
                        from sensor and actuator telemetry, then flag observations whose
                        patterns deviate from that learned baseline.
                    </p>
                </div>
                <div className="about-column">
                    <h3>How it works</h3>
                    <p>
                        A temporal convolutional autoencoder is trained on normal
                        operation only. Each 30-observation window is reconstructed, and
                        the reconstruction error becomes an anomaly score that is
                        compared against a frozen threshold.
                    </p>
                </div>
                <div className="about-column">
                    <h3>Scope</h3>
                    <p>
                        Research prototype for historical replay. Not connected to any
                        live plant. No control actions. Alerts are advisory and require
                        human review.
                    </p>
                </div>
            </div>
        </section>
    );
}