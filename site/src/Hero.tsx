import { motion, useReducedMotion } from "framer-motion";
import { useEffect, useState } from "react";

// Hand-built hero: a price tag tied with string to a newspaper masthead. The tag shows the measured number.
export function PriceTag({ label }: { label: string }) {
  const reduce = useReducedMotion();
  return (
    <svg viewBox="0 0 360 300" role="img" aria-label={`A price tag tied to a newspaper masthead showing ${label}`} className="w-full max-w-[360px] h-auto">
      <g fill="none" stroke="#15171A" strokeWidth="1.4" strokeLinecap="round">
        <rect x="20" y="20" width="320" height="64" rx="3" fill="#FFFFFF" fillOpacity=".6" />
        <line x1="34" y1="38" x2="326" y2="38" />
        <line x1="34" y1="44" x2="326" y2="44" strokeWidth=".6" />
        <text x="180" y="72" textAnchor="middle" fontFamily="Fraunces Variable, serif" fontSize="22" fill="#15171A" stroke="none" fontWeight="600">The Daily Ledger</text>
        {[0, 1, 2].map((i) => (<line key={i} x1={34 + i * 100} y1="92" x2={120 + i * 100} y2="92" strokeWidth=".6" />))}
      </g>
      <motion.g
        style={{ originX: "180px", originY: "84px" }}
        initial={reduce ? false : { rotate: 14 }}
        animate={{ rotate: 0 }}
        transition={reduce ? { duration: 0 } : { type: "spring", stiffness: 40, damping: 5, mass: 1.2 }}
      >
        <path d="M180 84 C 176 120, 190 140, 180 170" fill="none" stroke="#15171A" strokeWidth="1.4" />
        <path d="M180 170 L 120 184 L 120 270 Q 120 280 130 280 L 230 280 Q 240 280 240 270 L 240 184 Z" fill="#C8F25A" stroke="#15171A" strokeWidth="1.6" strokeLinejoin="round" />
        <circle cx="180" cy="190" r="5" fill="#F3F2EC" stroke="#15171A" strokeWidth="1.4" />
        <text x="180" y="236" textAnchor="middle" fontFamily="Fraunces Variable, serif" fontSize="26" fontWeight="600" fill="#15171A" className="num">{label}</text>
        <text x="180" y="258" textAnchor="middle" fontFamily="Instrument Sans, sans-serif" fontSize="9" letterSpacing="1.6" fill="#15171A">FLOOR PRICE</text>
      </motion.g>
    </svg>
  );
}

export function CountUp({ to, format }: { to: number; format: (v: number) => string }) {
  const reduce = useReducedMotion();
  const [v, setV] = useState(reduce ? to : 0);
  useEffect(() => {
    if (reduce) { setV(to); return; }
    let raf = 0; const t0 = performance.now(); const dur = 1400;
    const tick = (t: number) => { const p = Math.min(1, (t - t0) / dur); setV(to * (1 - Math.pow(1 - p, 3))); if (p < 1) raf = requestAnimationFrame(tick); };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [to, reduce]);
  return <span className="num">{format(v)}</span>;
}
