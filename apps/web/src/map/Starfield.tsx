import { useEffect, useRef } from "react";
import { skyOffset } from "./skyOffset";

type Star = {
  x: number;
  y: number;
  depth: number;
  r: number;
  alpha: number;
  phase: number;
  speed: number;
  twinkle: boolean;
  warm: boolean;
  bright: boolean;
};

function rng(seed: number) {
  // mulberry32: same sky on every load and resize
  return () => {
    seed |= 0;
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function makeStars(w: number, h: number): Star[] {
  const rand = rng(20260929);
  const count = Math.min(760, Math.max(160, Math.round((w * h) / 3000)));
  return Array.from({ length: count }, () => {
    const depth = 0.15 + rand() * 0.85;
    const bright = rand() < 0.018;
    return {
      x: rand() * w,
      y: rand() * h,
      depth,
      r: bright ? 1.1 + depth * 0.6 : 0.35 + depth * depth * 1.15,
      alpha: bright ? 0.95 : 0.3 + depth * 0.6,
      phase: rand() * Math.PI * 2,
      speed: 0.5 + rand() * 1.4,
      twinkle: bright || rand() < 0.35,
      warm: rand() < 0.12,
      bright,
    };
  });
}

export function Starfield() {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current!;
    const ctx = canvas.getContext("2d")!;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
    let stars: Star[] = [];
    let w = 0,
      h = 0,
      raf = 0,
      last = 0;

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = window.innerWidth;
      h = window.innerHeight;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      stars = makeStars(w, h);
      draw(performance.now());
    };

    const draw = (now: number) => {
      ctx.clearRect(0, 0, w, h);
      const t = now / 1000;
      for (const s of stars) {
        // Nearer stars drift more as the globe turns; wrapping keeps the field endless.
        const x = (((s.x - skyOffset.lng * s.depth * 2.2) % w) + w) % w;
        const y = (((s.y + skyOffset.lat * s.depth * 2.2) % h) + h) % h;
        const a = s.alpha * (s.twinkle && !reduce.matches ? 0.72 + 0.28 * Math.sin(t * s.speed + s.phase) : 1);
        const rgb = s.warm ? "255,222,180" : "214,228,255";
        if (s.bright) {
          const glow = ctx.createRadialGradient(x, y, 0, x, y, s.r * 2.8);
          glow.addColorStop(0, `rgba(${rgb},${a * 0.22})`);
          glow.addColorStop(1, `rgba(${rgb},0)`);
          ctx.fillStyle = glow;
          ctx.fillRect(x - s.r * 2.8, y - s.r * 2.8, s.r * 5.6, s.r * 5.6);
        }
        ctx.fillStyle = `rgba(${rgb},${a})`;
        ctx.beginPath();
        ctx.arc(x, y, s.r, 0, Math.PI * 2);
        ctx.fill();
      }
    };

    const loop = (now: number) => {
      raf = requestAnimationFrame(loop);
      if (now - last < 33) return; // ~30 fps is plenty for slow twinkle
      last = now;
      draw(now);
    };

    resize();
    if (!reduce.matches) raf = requestAnimationFrame(loop);
    window.addEventListener("resize", resize);
    const onPref = () => {
      cancelAnimationFrame(raf);
      if (reduce.matches) draw(performance.now());
      else raf = requestAnimationFrame(loop);
    };
    reduce.addEventListener("change", onPref);
    // Reduced motion draws once; camera moves still need a redraw so the sky stays coherent.
    const still = () => {
      if (reduce.matches) draw(performance.now());
    };
    window.addEventListener("iow:camera", still);

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
      window.removeEventListener("iow:camera", still);
      reduce.removeEventListener("change", onPref);
    };
  }, []);

  return <canvas ref={ref} className="starfield" aria-hidden="true" />;
}
