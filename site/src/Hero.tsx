import { motion, useAnimationControls, useMotionValue, useReducedMotion, useSpring, useTransform } from "framer-motion";
import { useEffect, useRef } from "react";

// Hand-built hero: a price tag tied with string to a newspaper masthead, with a receipt and a ledger floating behind.
// One signature motion: the tag swings once and settles, then idles with a faint sway. Pointer parallax on desktop.
export function HeroScene({ label }: { label: string }) {
  const reduce = useReducedMotion();
  const tag = useAnimationControls();
  const wrap = useRef<HTMLDivElement>(null);
  const px = useMotionValue(0), py = useMotionValue(0);
  const sx = useSpring(px, { stiffness: 60, damping: 18 }), sy = useSpring(py, { stiffness: 60, damping: 18 });
  const bx = useTransform(sx, (v) => v * -14), by = useTransform(sy, (v) => v * -10);
  const fx = useTransform(sx, (v) => v * 10), fy = useTransform(sy, (v) => v * 8);

  useEffect(() => {
    if (reduce) return;
    let live = true;
    (async () => {
      await tag.start({ rotate: [15, -7, 4, -2, 1, 0], transition: { duration: 2.6, ease: "easeOut" } });
      if (live) tag.start({ rotate: [0, 1.6, 0, -1.6, 0], transition: { duration: 7, repeat: Infinity, ease: "easeInOut" } });
    })();
    return () => { live = false; tag.stop(); };
  }, [reduce, tag]);

  const onMove = (e: React.PointerEvent) => {
    if (reduce || e.pointerType === "touch" || !wrap.current) return;
    const r = wrap.current.getBoundingClientRect();
    px.set((e.clientX - r.left) / r.width - 0.5);
    py.set((e.clientY - r.top) / r.height - 0.5);
  };

  return (
    <div ref={wrap} onPointerMove={onMove} onPointerLeave={() => { px.set(0); py.set(0); }} className="relative w-full max-w-[540px] mx-auto">
      <div aria-hidden className="absolute inset-[8%] rounded-[40px] bg-gradient-to-br from-white/70 to-sky-200/40 blur-2xl" />
      <svg viewBox="0 0 540 460" role="img" aria-label={`A price tag tied to a newspaper masthead, showing the measured floor price ${label}`} className="relative w-full h-auto overflow-visible">
        <defs>
          <linearGradient id="tagfill" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#D9F77E" /><stop offset="1" stopColor="#B7E64A" /></linearGradient>
          <linearGradient id="plate" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#FFFFFF" /><stop offset="1" stopColor="#EAF3FE" /></linearGradient>
          <filter id="soft" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="14" stdDeviation="14" floodColor="#0B3C82" floodOpacity=".22" /></filter>
        </defs>
        {/* back layer: receipt */}
        <motion.g style={{ x: bx, y: by }}>
          <g transform="translate(34 168) rotate(-8)" filter="url(#soft)">
            <rect width="132" height="176" rx="10" fill="url(#plate)" stroke="#0B1B33" strokeOpacity=".16" />
            <text x="14" y="26" fontFamily="JetBrains Mono, monospace" fontSize="9" fill="#0B1B33" opacity=".7">RECEIPT</text>
            {[44, 60, 76, 92].map((y, i) => <rect key={y} x="14" y={y} width={[92, 70, 84, 58][i]} height="5" rx="2.5" fill="#0B1B33" opacity=".14" />)}
            <rect x="14" y="116" width="104" height="1" fill="#0B1B33" opacity=".2" />
            <text x="14" y="138" fontFamily="JetBrains Mono, monospace" fontSize="8" fill="#0B4A99">sha256 7f3a9c…e1</text>
            <rect x="14" y="148" width="40" height="14" rx="7" fill="#C8F25A" />
            <text x="22" y="158" fontFamily="Geist Variable, sans-serif" fontSize="8" fontWeight="700" fill="#0B1B33">VERIFIED</text>
          </g>
        </motion.g>
        {/* back layer: ledger */}
        <motion.g style={{ x: fx, y: fy }}>
          <g transform="translate(372 250) rotate(7)" filter="url(#soft)">
            <rect width="140" height="150" rx="12" fill="url(#plate)" stroke="#0B1B33" strokeOpacity=".16" />
            <text x="14" y="24" fontFamily="Geist Variable, sans-serif" fontSize="9" fontWeight="700" letterSpacing="1.4" fill="#3A4A66">HONEST WAIT</text>
            {[0, 1, 2, 3].map((i) => (<g key={i}><rect x="14" y={42 + i * 24} width="112" height="9" rx="4.5" fill="#0B1B33" opacity=".07" /><rect x="14" y={42 + i * 24} width={[30, 52, 76, 98][i]} height="9" rx="4.5" fill={i === 3 ? "#0F5B4F" : "#5E9AD8"} /></g>))}
          </g>
        </motion.g>
        {/* masthead */}
        <g filter="url(#soft)">
          <rect x="90" y="22" width="360" height="92" rx="14" fill="url(#plate)" stroke="#0B1B33" strokeOpacity=".18" />
          <line x1="110" y1="44" x2="430" y2="44" stroke="#0B1B33" strokeWidth="1.6" />
          <line x1="110" y1="50" x2="430" y2="50" stroke="#0B1B33" strokeWidth=".7" />
          <text x="270" y="88" textAnchor="middle" fontFamily="Newsreader Variable, Georgia, serif" fontSize="34" fontWeight="600" letterSpacing="-0.5" fill="#0B1B33">The Daily Ledger</text>
          <line x1="110" y1="100" x2="430" y2="100" stroke="#0B1B33" strokeWidth=".7" />
          <circle cx="118" cy="35" r="3.2" fill="#C8F25A" stroke="#0B1B33" strokeWidth=".8" />
        </g>
        {/* tag on string */}
        <motion.g style={{ originX: "270px", originY: "114px" }} animate={tag} initial={reduce ? false : { rotate: 15 }}>
          <path d="M270 114 C 266 150, 282 168, 270 206" fill="none" stroke="#0B1B33" strokeWidth="1.7" strokeLinecap="round" />
          <g filter="url(#soft)">
            <path d="M270 206 L196 224 L196 396 Q196 414 214 414 L326 414 Q344 414 344 396 L344 224 Z" fill="url(#tagfill)" stroke="#0B1B33" strokeWidth="1.8" strokeLinejoin="round" />
          </g>
          <circle cx="270" cy="232" r="6.5" fill="#EAF4FF" stroke="#0B1B33" strokeWidth="1.6" />
          <path d="M216 396 L324 396" stroke="#0B1B33" strokeWidth="1" strokeDasharray="3 4" opacity=".4" />
          <text x="270" y="288" textAnchor="middle" fontFamily="Geist Variable, sans-serif" fontSize="10" fontWeight="700" letterSpacing="2.2" fill="#0B1B33" opacity=".75">FLOOR PRICE</text>
          <text x="270" y="344" textAnchor="middle" fontFamily="Newsreader Variable, Georgia, serif" fontSize={label.length > 7 ? 34 : label.length > 5 ? 40 : 46} fontWeight="600" letterSpacing="-1" fill="#0B1B33">{label}</text>
          <text x="270" y="378" textAnchor="middle" fontFamily="Geist Variable, sans-serif" fontSize="10" fill="#0B1B33" opacity=".75">cheapest priced attack</text>
        </motion.g>
        {/* floating coins */}
        {[[92, 150, 7, 0], [452, 176, 5, 1.2], [150, 410, 6, 0.6]].map(([x, y, r, d], i) => (
          <motion.circle key={i} cx={x} cy={y} r={r} fill="#C8F25A" stroke="#0B1B33" strokeWidth="1.3" animate={reduce ? undefined : { y: [0, -8, 0] }} transition={{ duration: 4 + i, repeat: Infinity, ease: "easeInOut", delay: d }} />
        ))}
      </svg>
    </div>
  );
}
