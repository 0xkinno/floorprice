import { animate, motion, useInView, useReducedMotion } from "framer-motion";
import { useEffect, useRef, useState, type ReactNode } from "react";

export function Reveal({ children, delay = 0, y = 18, className = "" }: { children: ReactNode; delay?: number; y?: number; className?: string }) {
  const reduce = useReducedMotion();
  return (
    <motion.div className={className} initial={reduce ? false : { opacity: 0, y }} whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-60px" }} transition={{ duration: 0.55, delay, ease: [0.2, 0.8, 0.2, 1] }}>
      {children}
    </motion.div>
  );
}

export function Stagger({ children, className = "" }: { children: ReactNode; className?: string }) {
  const reduce = useReducedMotion();
  return (
    <motion.div className={className} initial={reduce ? false : "hidden"} whileInView="show" viewport={{ once: true, margin: "-60px" }}
      variants={{ hidden: {}, show: { transition: { staggerChildren: 0.09 } } }}>
      {children}
    </motion.div>
  );
}
export const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.2, 0.8, 0.2, 1] as number[] } } };

export function CountUp({ to, format, className = "" }: { to: number; format: (v: number) => string; className?: string }) {
  const reduce = useReducedMotion();
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-40px" });
  const [v, setV] = useState(reduce ? to : 0);
  useEffect(() => {
    if (reduce) { setV(to); return; }
    if (!inView) return;
    const c = animate(0, to, { duration: 1.3, ease: [0.16, 1, 0.3, 1], onUpdate: setV });
    return () => c.stop();
  }, [to, inView, reduce]);
  return <span ref={ref} className={"num " + className}>{format(v)}</span>;
}

export function Chip({ sim }: { sim: boolean }) {
  return <span className={"chip " + (sim ? "" : "chip-real")}><span aria-hidden className={"inline-block w-1.5 h-1.5 rounded-full " + (sim ? "bg-azure" : "bg-lime")} />{sim ? "Simulated" : "Real"}</span>;
}

export function Eyebrow({ n, children }: { n?: string; children: ReactNode }) {
  return <p className="label flex items-center gap-3 m-0 mb-3">{n && <span className="num font-mono text-[11px] tracking-normal px-1.5 py-0.5 rounded bg-white/70 border border-[var(--line)]">{n}</span>}{children}</p>;
}

export const Display = ({ children, className = "" }: { children: ReactNode; className?: string }) => (
  <h2 className={"font-display font-medium leading-[1.04] m-0 text-[clamp(2.1rem,4.6vw,3.6rem)] " + className}>{children}</h2>
);

const P = { fill: "none", stroke: "currentColor", strokeWidth: 1.6, strokeLinecap: "round", strokeLinejoin: "round" } as const;
export function TechIcon({ id }: { id: string }) {
  const k = id.split(" ")[0];
  const g: Record<string, ReactNode> = {
    T1: <><path {...P} d="M5 5h14M5 10h14M5 15h9" /><path {...P} d="m15.5 18 1.8 1.8 3.4-3.8" /></>,
    T2: <path {...P} d="M5 6.5A2.5 2.5 0 0 1 7.5 4h9A2.5 2.5 0 0 1 19 6.5v6a2.5 2.5 0 0 1-2.5 2.5H11l-4 4v-4h-.5A2.5 2.5 0 0 1 5 12.5z" />,
    T3: <><path {...P} d="M7 3h7l4 4v14H7z" /><path {...P} d="M14 3v4h4M9.5 12h6M9.5 15.5h6" /></>,
    T4: <><circle {...P} cx="6" cy="7" r="2" /><circle {...P} cx="18" cy="6" r="2" /><circle {...P} cx="12" cy="17" r="2.4" /><path {...P} d="m7.8 8 3 7M16.4 7.4l-3 7.8M8 7h8" /></>,
    T5: <><rect {...P} x="9" y="8" width="11" height="11" rx="2" /><path {...P} d="M6 16V6a2 2 0 0 1 2-2h8" /></>,
    T6a: <><path {...P} d="M5 5h11a3 3 0 0 1 3 3v11H8a3 3 0 0 1-3-3z" /><path {...P} d="M9 10h6M9 14h4" /></>,
    T6b: <><path {...P} d="M5 5h11a3 3 0 0 1 3 3v11H8a3 3 0 0 1-3-3z" /><path {...P} d="m9 14 2.2-2.4 2 1.8L16 9.5" /></>,
    T7: <><circle {...P} cx="9.5" cy="12" r="5.5" /><circle {...P} cx="14.5" cy="12" r="5.5" /></>,
    "C*": <><path {...P} d="M12 3.5 19 6v5.5c0 4.2-2.8 7.2-7 9-4.2-1.8-7-4.8-7-9V6z" /><path {...P} d="m9 12 2.2 2.2L15.5 10" /></>,
  };
  return <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false">{g[k] ?? g.T1}</svg>;
}

export const Arrow = () => (<svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true"><path d="M4 10h11m0 0-4.5-4.5M15 10l-4.5 4.5" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg>);

export const TECH_LINE: Record<string, string> = {
  T1: "Look the domain up in an expert list.",
  T2: "Ask a language model from the name alone.",
  T3: "Ask a language model with the source's own page.",
  T4: "Rank sources by who links to them.",
  T5: "Count independent sources repeating a claim.",
  T6a: "Score a track record by how often a source was right.",
  T6b: "Score a track record against what the crowd already knew.",
  T7: "Show what people who usually disagree both rate helpful.",
  "C*": "Track record gated by bridging; the model can only lower a score.",
  "T7 majority vote": "Show a note when most raters call it helpful.",
  "T4 PageRank": "Rank sources by how many sources link to them.",
  "T4 TrustRank": "Rank by links, trusting only what flows from vetted seeds.",
  "T7 bridging": "Show a note only when people who usually disagree both rate it helpful.",
};
