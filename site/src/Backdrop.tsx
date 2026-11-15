import { motion, useReducedMotion } from "framer-motion";

// Slow aurora behind everything. Static when the visitor prefers reduced motion.
export function Backdrop() {
  const reduce = useReducedMotion();
  const blob = (cls: string, x: number[], y: number[], d: number) => (
    <motion.div aria-hidden className={"absolute rounded-full blur-3xl " + cls} animate={reduce ? undefined : { x, y }} transition={{ duration: d, repeat: Infinity, repeatType: "mirror", ease: "easeInOut" }} />
  );
  return (
    <div aria-hidden className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      {blob("w-[46vw] h-[46vw] -top-[14vw] right-[-8vw] bg-white/70", [0, -40, 20], [0, 30, -10], 22)}
      {blob("w-[38vw] h-[38vw] top-[28vh] -left-[12vw] bg-sky-400/40", [0, 50, 10], [0, -30, 20], 26)}
      {blob("w-[30vw] h-[30vw] bottom-[-10vw] right-[12vw] bg-lime/25", [0, -30, 0], [0, -20, 10], 30)}
      <div className="absolute inset-0 opacity-[.5]" style={{ backgroundImage: "radial-gradient(rgba(11,74,153,.16) 1px, transparent 1.2px)", backgroundSize: "26px 26px", maskImage: "linear-gradient(180deg, #000 0%, transparent 70%)", WebkitMaskImage: "linear-gradient(180deg, #000 0%, transparent 70%)" }} />
    </div>
  );
}
