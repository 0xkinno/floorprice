import { motion, useReducedMotion } from "framer-motion";
import { Row, cheapestUsd, isSim, money, native, unpricedCrossing } from "./data";
import { Chip, TechIcon } from "./ui";

const LO = -3, HI = 5;   // log10 dollars: $0.001 to $100,000
const pct = (v: number) => Math.min(100, Math.max(0, ((Math.log10(Math.max(v, 1e-3)) - LO) / (HI - LO)) * 100));
const TICKS = [-3, -1, 1, 3, 5];

// The floor ladder: how much each technique costs to cross, on a log-dollar axis, with an optional budget needle.
export function Ladder({ rows, level, budget }: { rows: Row[]; level: "low" | "mid" | "high"; budget?: number }) {
  const reduce = useReducedMotion();
  return (
    <div className="glass p-5 sm:p-7">
      <div className="relative" style={{ ["--lad-off" as string]: "min(11.5rem, 34%)" }}>
        {budget !== undefined && (
          <div aria-hidden className="absolute top-0 bottom-7 z-10 pointer-events-none" style={{ left: "calc(var(--lad-off) + 0.75rem)", right: 0 }}>
            <motion.div className="absolute top-0 h-full" initial={false} animate={{ left: `${pct(budget)}%` }} transition={reduce ? { duration: 0 } : { type: "spring", stiffness: 140, damping: 22 }}>
              <div className="w-px h-full bg-ink/70" />
              <span className="absolute top-0 -translate-x-1/2 -translate-y-[130%] chip chip-real num whitespace-nowrap">Budget {money(budget)}</span>
            </motion.div>
          </div>
        )}
        <ul role="list" className={"m-0 p-0 list-none grid gap-3 " + (budget !== undefined ? "pt-8" : "")}>
          {rows.map((r, i) => {
            const v = cheapestUsd(r, level);
            const sim = isSim(r.technique);
            const flips = budget !== undefined && typeof v === "number" && v <= budget;
            const un = unpricedCrossing(r);
            return (
              <li key={r.technique} className="grid items-center gap-3" style={{ gridTemplateColumns: "var(--lad-off) 1fr" }}>
                <div className="flex items-center gap-2 min-w-0 text-ink">
                  <span className="shrink-0 grid place-items-center w-8 h-8 rounded-[10px] bg-white/80 border border-[var(--line)]"><TechIcon id={r.technique} /></span>
                  <span className="text-[13px] font-semibold leading-tight">{r.technique}</span>
                </div>
                <div className="relative h-8 rounded-full bg-ink/[.06] overflow-hidden">
                  {typeof v === "number" ? (
                    <motion.div className={"absolute inset-y-0 left-0 rounded-full " + (flips ? "bg-ember" : "bg-gradient-to-r from-azure to-sky-500")}
                      initial={reduce ? false : { width: 0 }} whileInView={{ width: `${Math.max(pct(v), 2)}%` }} viewport={{ once: true }} transition={{ duration: 0.9, delay: i * 0.05, ease: [0.16, 1, 0.3, 1] }}>
                      {sim && <div className="absolute inset-0 rounded-full hatch-sim" />}
                    </motion.div>
                  ) : v === "inf" ? (
                    <div className="absolute inset-0 hatch rounded-full" />
                  ) : (
                    <div className="absolute inset-0 rounded-full border border-dashed border-ink/30" />
                  )}
                  <span className="absolute inset-y-0 right-3 flex items-center text-[12px] font-semibold num text-ink/90 mix-blend-normal">
                    {typeof v === "number" ? <span className="px-1.5 rounded bg-white/85">{money(v)}</span> : <span className="px-1.5 rounded bg-white/85">{v === "inf" ? "no priced attack crosses" : "unpriced"}</span>}
                  </span>
                </div>
                <span className="sr-only">{r.technique}: {money(v)}{budget !== undefined && typeof v === "number" ? (flips ? ", flips at your budget" : ", holds at your budget") : ""}{un.map((u) => `, unpriced ${u.name} crosses at ${u.native} ${u.unit}s`).join("")}</span>
              </li>
            );
          })}
        </ul>
        <div className="grid mt-3 gap-3" style={{ gridTemplateColumns: "var(--lad-off) 1fr" }} aria-hidden>
          <span />
          <div className="relative h-5 num text-[11px] text-[var(--muted)]">
            {TICKS.map((t) => (<span key={t} className="absolute -translate-x-1/2" style={{ left: `${((t - LO) / (HI - LO)) * 100}%` }}>{t >= 3 ? `$${Math.pow(10, t) / 1000}k` : `$${Math.pow(10, t)}`}</span>))}
          </div>
        </div>
      </div>
      <p className="text-[13px] text-[var(--muted)] mt-4 mb-0 max-w-3xl">
        <span className="label">Fig. 1</span>&nbsp; Cheapest priced attack found per technique at {level} prices, log dollars. Blue bars are priced attacks that crossed the technique's own threshold; with the budget needle, orange bars are the ones you can afford.
        Hatched teal means no priced attack crossed within the cap. Fine stripes mark simulations. Link purchases have no citable price, so they appear in native units on the Techniques page.
      </p>
    </div>
  );
}
