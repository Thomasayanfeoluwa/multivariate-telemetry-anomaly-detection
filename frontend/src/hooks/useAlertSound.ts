import { useCallback, useEffect, useRef, useState } from "react";

const STORAGE_KEY = "swat.alertSound.enabled";
const MIN_INTERVAL_MS = 800;

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
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.value = 880;
      gain.gain.value = 0.12;
      osc.connect(gain);
      gain.connect(ctx.destination);
      const t0 = ctx.currentTime;
      osc.start(t0);
      gain.gain.setValueAtTime(0.12, t0);
      gain.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.15);
      osc.stop(t0 + 0.16);
    } catch {
      // Silent failure — sound is a nice-to-have
    }
  }, [enabled]);

  const toggle = useCallback(() => {
    setEnabled((v) => !v);
  }, []);

  return { enabled, toggle, play };
}