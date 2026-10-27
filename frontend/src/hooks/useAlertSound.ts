import { useCallback, useEffect, useRef, useState } from "react";

const STORAGE_KEY = "swat.alertSound.enabled";
const MIN_INTERVAL_MS = 500;

export interface UseAlertSound {
  enabled: boolean;
  toggle: () => void;
  play: () => void;
}

export function useAlertSound(): UseAlertSound {
  const [enabled, setEnabled] = useState<boolean>(() => {
    try {
      const v = localStorage.getItem(STORAGE_KEY);
      return v === null ? true : v === "true";
    } catch {
      return true;
    }
  });

  const ctxRef = useRef<AudioContext | null>(null);
  const lastPlayedRef = useRef<number>(0);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, String(enabled));
    } catch {
      // ignore
    }
  }, [enabled]);

  const play = useCallback(() => {
    if (!enabled) return;
    const now = Date.now();
    if (now - lastPlayedRef.current < MIN_INTERVAL_MS) return;
    lastPlayedRef.current = now;

    try {
      if (ctxRef.current === null) {
        const Ctor =
          window.AudioContext ??
          (window as unknown as { webkitAudioContext?: typeof AudioContext })
            .webkitAudioContext;
        if (!Ctor) return;
        ctxRef.current = new Ctor();
      }
      const ctx = ctxRef.current;
      if (ctx.state === "suspended") {
        void ctx.resume();
      }

      // Industrial-style alarm: three rapid square-wave pulses at 880 Hz.
      // Duration ~420 ms total. Peak gain 0.18 (clearly audible without being
      // shrill). Rate limit above prevents overlapping alarms if two episodes
      // start close together.
      const pulses = 3;
      const pulseSec = 0.1;
      const gapSec = 0.06;
      const peakGain = 0.18;
      const startAt = ctx.currentTime + 0.01;

      for (let i = 0; i < pulses; i++) {
        const t0 = startAt + i * (pulseSec + gapSec);
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = "square";
        osc.frequency.value = 880;

        gain.gain.setValueAtTime(0.0001, t0);
        gain.gain.linearRampToValueAtTime(peakGain, t0 + 0.008);
        gain.gain.setValueAtTime(peakGain, t0 + pulseSec - 0.012);
        gain.gain.exponentialRampToValueAtTime(0.0001, t0 + pulseSec);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start(t0);
        osc.stop(t0 + pulseSec + 0.01);
      }
    } catch {
      // Silent failure — sound is a nice-to-have
    }
  }, [enabled]);

  const toggle = useCallback(() => {
    setEnabled((v) => !v);
  }, []);

  return { enabled, toggle, play };
}