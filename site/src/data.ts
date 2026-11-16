export type Usd = { low: number | "inf"; mid: number | "inf"; high: number | "inf" } | null;
export type Attack = { native: number | "inf" | null; unit: string; usd: Usd; note?: string };
export type Row = {
  technique: string;
  attacks: Record<string, Attack>;
  honest_wait: { native: number | "inf" | null; unit: string; days: Record<string, number | "inf"> | null; note?: string };
};
export type Site = {
  table: Row[];
  hypotheses: Record<string, any>;
  audit: any;
  pending: string[];
  prices: any;
  honest_rates: Record<string, Record<string, number>>;
  llm?: any;
  e5?: any;
  lock: { combined: string; locked_at: string; first_combined: string; first_locked_at: string; amendments: number };
  sample_receipt: Record<string, any>;
};

export async function loadSite(): Promise<Site> {
  const r = await fetch("./data/site.json");
  return r.json();
}

export const SIMULATED = ["T4", "T5", "T6a", "T6b", "T7", "C*"];
export const isSim = (name: string) => SIMULATED.includes(name.split(" ")[0]);

export function cheapestUsd(row: Row, level: "low" | "mid" | "high"): number | null | "inf" {
  let best: number | null | "inf" = null;
  for (const a of Object.values(row.attacks)) {
    if (!a.usd) continue;
    const v = a.usd[level];
    if (v === "inf") { if (best === null) best = "inf"; continue; }
    if (best === null || best === "inf" || v < best) best = v;
  }
  return best;
}

export function money(v: number | null | "inf"): string {
  if (v === null) return "unpriced";
  if (v === "inf") return "no priced attack crosses";
  if (v < 0.01) return "under $0.01";
  if (v < 100) return "$" + v.toFixed(2);
  return "$" + Math.round(v).toLocaleString("en-US");
}

export function native(a: number | "inf" | null | undefined, unit: string): string {
  if (a === null || a === undefined) return "pending";
  if (a === "inf") return "never observed";
  return `${Number.isInteger(a) ? a : a.toFixed(1)} ${unit}${a === 1 ? "" : "s"}`;
}

export function headline(site: Site): { value: number; name: string } | null {
  let best: { value: number; name: string } | null = null;
  for (const r of site.table) {
    const v = cheapestUsd(r, "mid");
    if (typeof v === "number" && (best === null || v < best.value)) best = { value: v, name: r.technique };
  }
  return best;
}

export function unpricedCrossing(row: Row): { name: string; native: number; unit: string }[] {
  return Object.entries(row.attacks)
    .filter(([, a]) => a.usd === null && typeof a.native === "number")
    .map(([k, a]) => ({ name: k.replace(/_/g, " "), native: a.native as number, unit: a.unit }));
}
