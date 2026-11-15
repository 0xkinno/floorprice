import { useEffect, useMemo, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis, LabelList } from "recharts";
import { CountUp, PriceTag } from "./Hero";
import { Row, Site, cheapestUsd, headline, isSim, loadSite, money, native, unpricedCrossing } from "./data";

const PAGES = [
  ["findings", "Findings"], ["price", "Price an attack"], ["techniques", "Techniques"], ["method", "Method"], ["paper", "Paper"],
] as const;
type Page = (typeof PAGES)[number][0];

function useHash(): [Page, (p: Page) => void] {
  const get = (): Page => { const h = window.location.hash.replace("#/", ""); return (PAGES.find((p) => p[0] === h)?.[0] ?? "findings") as Page; };
  const [p, setP] = useState<Page>(get);
  useEffect(() => { const f = () => setP(get()); window.addEventListener("hashchange", f); return () => window.removeEventListener("hashchange", f); }, []);
  return [p, (n) => { window.location.hash = "#/" + n; }];
}

function Nav({ page, go }: { page: Page; go: (p: Page) => void }) {
  return (
    <header className="sticky top-3 z-20 px-4">
      <nav aria-label="Main" className="mx-auto max-w-5xl flex items-center justify-between gap-3 rounded-[14px] border border-hair bg-paper/80 backdrop-blur px-3 py-2">
        <ul className="flex flex-wrap gap-x-1 gap-y-1 m-0 p-0 list-none">
          {PAGES.map(([id, label]) => (
            <li key={id}>
              <a href={"#/" + id} onClick={(e) => { e.preventDefault(); go(id); }} aria-current={page === id ? "page" : undefined}
                 className={"px-2.5 py-1.5 rounded-[10px] text-sm no-underline " + (page === id ? "bg-lime text-ink font-semibold" : "text-ink hover:bg-white/70")}>{label}</a>
            </li>
          ))}
        </ul>
        <a href="#/paper" onClick={(e) => { e.preventDefault(); go("paper"); }} className="hidden sm:inline-block shrink-0 rounded-[10px] bg-ink text-paper no-underline px-3 py-1.5 text-sm font-semibold">Read the paper</a>
      </nav>
    </header>
  );
}

const H2 = ({ children, id }: { children: React.ReactNode; id?: string }) => <h2 id={id} className="font-display text-3xl sm:text-4xl leading-tight mt-0 mb-3">{children}</h2>;

function Tag({ sim }: { sim: boolean }) {
  return <span className={"label inline-block rounded px-1.5 py-0.5 border " + (sim ? "border-hair" : "border-moss text-moss")}>{sim ? "simulated" : "real"}</span>;
}

function FloorChart({ rows, level }: { rows: Row[]; level: "low" | "mid" | "high" }) {
  const data = rows.map((r) => {
    const v = cheapestUsd(r, level);
    return { name: r.technique, v: typeof v === "number" ? Math.max(v, 0.001) : v === "inf" ? 1e6 : null, inf: v === "inf", unpriced: v === null, sim: isSim(r.technique) };
  }).filter((d) => d.v !== null);
  return (
    <figure className="m-0">
      <div role="img" aria-label="Bar chart of the cheapest priced attack per technique, log dollars" style={{ height: Math.max(220, data.length * 38) }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ left: 8, right: 56 }}>
            <XAxis type="number" scale="log" domain={[0.001, 1e6]} tickFormatter={(v) => (v >= 1000 ? `$${v / 1000}k` : `$${v}`)} ticks={[0.001, 0.1, 10, 1000, 100000]} tick={{ fontSize: 11, fill: "#15171A" }} />
            <YAxis type="category" dataKey="name" width={150} tick={{ fontSize: 11, fill: "#15171A" }} />
            <Tooltip formatter={(v: number, _n, p) => (p.payload.inf ? "no crossing observed" : money(v))} />
            <Bar dataKey="v" isAnimationActive={false}>
              {data.map((d, i) => <Cell key={i} fill={d.inf ? "#3E5B2A" : "#D9542B"} fillOpacity={d.sim ? 0.65 : 1} />)}
              <LabelList dataKey="v" position="right" formatter={(v: number) => (v >= 1e6 ? "no priced attack" : money(v))} style={{ fontSize: 11, fill: "#15171A" }} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <figcaption className="text-sm text-[color:var(--muted)] mt-2">
        <span className="label">Figure 1</span> Cheapest priced attack per technique at {level} prices, log dollars. Ember bars are priced attacks that crossed the threshold; moss bars
        mean no priced attack crossed within the cap (unpriced link purchases may still cross, see the Techniques page). Lighter bars are simulations; solid bars are real model measurements. Links are unpriced and omitted.
      </figcaption>
    </figure>
  );
}

function Findings({ site }: { site: Site }) {
  const reduce = useReducedMotion();
  const h = headline(site);
  const H = site.hypotheses;
  const items: { k: string; text: string; sim: boolean }[] = [];
  if (H.H5) items.push({ k: "H5", sim: true, text: `A long con crosses an accuracy track record in ${native(H.H5.con_T6a_median_articles, "article")}. Against a consensus-relative record it never crosses in 500, but an honest informed newcomer needs a median of ${native(H.H5.honest_T6b_median_claims, "claim")}.` });
  if (H.H6) items.push({ k: "H6", sim: true, text: `A false note passes majority vote with a median of ${native(H.H6.majority_median_accounts, "account")} and bridging with ${native(H.H6.bridging_median_accounts, "account")}.` });
  if (H.H7) items.push({ k: "H7", sim: true, text: `The composite C* inherits the bridging floor of ${native(H.H7.cstar_floor_accounts, "account")} by construction. Its honest wait is ${native(H.H7.honest_wait_cstar, "claim")} against ${native(H.H7.honest_wait_T6b, "claim")} for T6b alone, a difference within simulation noise.` });
  ["H1", "H2", "H3", "H4"].forEach((k) => { if (H[k]) items.push({ k, sim: false, text: `${k}: ${H[k].supported ? "supported" : "not supported"} on real model runs.` }); });
  const pendingLLM = site.pending.filter((p) => /^E\d/.test(p)).length > 0;
  return (
    <div>
      <section className="grid md:grid-cols-[1.2fr_1fr] gap-8 items-center pt-10 pb-8">
        <div>
          <p className="label">Floor price of trust</p>
          <h1 className="font-display text-4xl sm:text-6xl leading-[1.05] mt-2 mb-4">What it costs a liar to look reliable.</h1>
          <p className="text-lg max-w-xl mt-0">And how long an honest newcomer waits, under seven source-reliability scores. Dana Reyes, a fictional verification editor in Ohio, has to decide at 6:40am which of dozens of new local-news domains to trust.</p>
          {h && (
            <p className="mt-6 mb-0"><span className="label block mb-2">Cheapest priced attack found, mid prices</span>
              <span className="font-display text-5xl sm:text-6xl bg-lime px-2 rounded inline-block leading-tight"><CountUp to={h.value} format={(v) => (v < 0.01 ? "under $0.01" : "$" + (v < 100 ? v.toFixed(2) : Math.round(v).toLocaleString("en-US")))} /></span>
              <span className="block text-sm mt-2 text-[color:var(--muted)]">{h.name}{isSim(h.name) ? ", simulated" : ""}</span></p>
          )}
        </div>
        <div className="flex justify-center md:justify-end"><PriceTag label={h ? (h.value < 0.01 ? "<$0.01" : money(h.value)) : "pending"} /></div>
      </section>
      {pendingLLM && (
        <p role="note" className="rule pt-4 text-sm">Model-based results (techniques T2, T3 and the paraphrase attack) are still running. Pending items are marked, not filled in. Simulated results are labelled simulated.</p>
      )}
      <section className="rule pt-6 pb-6"><H2>Findings</H2>
        <motion.div className="grid gap-4 md:grid-cols-3" initial={reduce ? false : { opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}>
          {items.slice(0, 6).map((f) => (
            <article key={f.k} className="card p-4"><div className="flex justify-between items-center"><span className="label">{f.k}</span><Tag sim={f.sim} /></div><p className="mb-0 mt-2">{f.text}</p></article>
          ))}
        </motion.div>
      </section>
      <section className="rule pt-6 pb-10"><FloorChart rows={site.table} level="mid" /></section>
    </div>
  );
}

function PriceAttack({ site }: { site: Site }) {
  const [level, setLevel] = useState<"low" | "mid" | "high">("mid");
  const [exp, setExp] = useState(1);   // budget = 10^exp dollars
  const budget = Math.pow(10, exp);
  const rows = site.table;
  return (
    <div className="pt-10 pb-10">
      <p className="label">Price an attack</p>
      <H2>What does your budget buy?</H2>
      <p className="max-w-2xl mt-0">Pick a budget and a price assumption. Each row shows whether the cheapest priced attack found in our results fits inside it, and what an honest newcomer waits. Nothing here calls a model.</p>
      <div className="card p-4 grid gap-4 sm:grid-cols-[1fr_auto] items-end">
        <div>
          <label htmlFor="budget" className="label block mb-1">Budget <span className="num text-ink">{money(budget)}</span></label>
          <input id="budget" type="range" min={-2} max={5} step={0.05} value={exp} onChange={(e) => setExp(parseFloat(e.target.value))} className="w-full accent-[#3E5B2A]" aria-valuetext={money(budget)} />
        </div>
        <fieldset className="border-0 p-0 m-0"><legend className="label mb-1">Unit prices</legend>
          <div className="flex gap-1">{(["low", "mid", "high"] as const).map((l) => (
            <label key={l} className={"cursor-pointer rounded-[10px] px-3 py-1.5 border text-sm " + (level === l ? "bg-lime border-ink font-semibold" : "border-hair bg-white/60")}>
              <input type="radio" name="lvl" value={l} checked={level === l} onChange={() => setLevel(l)} className="sr-only" />{l}</label>))}</div>
        </fieldset>
      </div>
      <div className="overflow-x-auto mt-4" tabIndex={0} role="region" aria-label="Price table, scrollable">
        <table className="w-full text-sm border-collapse min-w-[560px]">
          <thead><tr className="text-left"><th className="label py-2 pr-3">Technique</th><th className="label pr-3">Cheapest priced attack</th><th className="label pr-3">At your budget</th><th className="label">Honest wait</th></tr></thead>
          <tbody>
            {rows.map((r) => {
              const v = cheapestUsd(r, level);
              const flips = typeof v === "number" && v <= budget;
              const wait = r.honest_wait;
              const days = wait.days ? wait.days[level] : null;
              return (
                <tr key={r.technique} className="rule align-top">
                  <th scope="row" className="py-2 pr-3 text-left font-semibold">{r.technique} <Tag sim={isSim(r.technique)} /></th>
                  <td className="pr-3 num">{money(v)}</td>
                  <td className="pr-3">{v === null ? <span>unpriced, see native units</span> : flips ? <strong className="text-embertext">flips</strong> : <strong className="text-moss">holds for priced attacks</strong>}
                    {unpricedCrossing(r).map((u) => (<span key={u.name} className="block text-embertext">unpriced: {u.name} crosses at {u.native} {u.unit}s</span>))}</td>
                  <td className="num">{native(wait.native as any, wait.unit)}{typeof days === "number" ? `, about ${days < 1 ? "under a day" : Math.round(days) + " days"} at assumed rates` : ""}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="text-sm mt-3 text-[color:var(--muted)]">Honest-wait times use assumed arrival rates (see Method). Native units are primary.</p>
    </div>
  );
}

function Techniques({ site }: { site: Site }) {
  const aud = site.audit?.scores as Record<string, { coder1: number; coder2: number }> | undefined;
  return (
    <div className="pt-10 pb-10">
      <p className="label">Techniques</p><H2>Seven ways to score a source</H2>
      <div className="grid gap-4 md:grid-cols-2">
        {site.table.map((r) => {
          const id = r.technique.split(" ")[0];
          const key = Object.keys(aud ?? {}).find((k) => k.startsWith(id + "|b"));
          return (
            <article key={r.technique} className="card p-4">
              <div className="flex justify-between items-start gap-2"><h3 className="font-display text-xl m-0">{r.technique}</h3><Tag sim={isSim(r.technique)} /></div>
              <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 mt-3 mb-0 text-sm">
                {Object.entries(r.attacks).map(([k, a]) => (<><dt key={k + "d"} className="label self-center">{k.replace(/_/g, " ")}</dt><dd key={k} className="m-0 num">{native(a.native as any, a.unit)}{a.usd ? `, ${money(a.usd.mid)}` : ""}</dd></>))}
                <dt className="label self-center">Honest wait</dt><dd className="m-0 num">{native(r.honest_wait.native as any, r.honest_wait.unit)}</dd>
                <dt className="label self-center">Auditability</dt><dd className="m-0">{key && aud ? `${Math.round(aud[key].coder1 * 6)} of 6 criteria` : "pending human coding"}</dd>
              </dl>
            </article>
          );
        })}
      </div>
      <section className="rule mt-8 pt-4"><h3 className="font-display text-xl mt-0">A sample receipt</h3>
        <p className="mt-0 max-w-2xl">Every technique emits one. It is a format, not a product claim. Anyone can recompute the digest from the other fields.</p>
        <pre className="font-mono text-xs bg-white/60 border border-hair rounded-[14px] p-4 overflow-x-auto" tabIndex={0}>{JSON.stringify(site.sample_receipt, null, 2)}</pre>
      </section>
    </div>
  );
}

function Method({ site }: { site: Site }) {
  const H = site.hypotheses;
  return (
    <div className="pt-10 pb-10">
      <p className="label">Method and pre-registration</p><H2>Written down before the first model call</H2>
      <p className="max-w-2xl mt-0">Hypotheses, prompts, parameters, sampled domains, fictional names, pages and prices were hashed into a lock file before any main model call. The runner refuses to run if they change unless an amendment is recorded.</p>
      <p className="font-mono text-xs break-all mb-6" tabIndex={0}>combined digest {site.lock.combined}<br />locked {site.lock.locked_at}</p>
      <table className="w-full text-sm border-collapse"><thead><tr className="text-left"><th className="label py-2">Hypothesis</th><th className="label">Result</th></tr></thead>
        <tbody>{["H1", "H2", "H3", "H4", "H5", "H6", "H7"].map((k) => (
          <tr key={k} className="rule"><th scope="row" className="py-2 text-left">{k}</th><td>{H[k] ? (H[k].supported ? "supported" : H[k].partly ? "partly supported" : "not supported") : "pending real-model runs"}</td></tr>))}</tbody></table>
      <p className="text-sm mt-4">H5 to H7 are simulation hypotheses and were not blind: simulators were tuned and read while being built, as disclosed in the paper.</p>
    </div>
  );
}

function Paper() {
  const [has, setHas] = useState<boolean | null>(null);
  useEffect(() => { fetch("./paper.pdf", { method: "HEAD" }).then((r) => setHas(r.ok && (r.headers.get("content-type") ?? "").includes("pdf"))).catch(() => setHas(false)); }, []);
  return (
    <div className="pt-10 pb-10"><p className="label">Paper</p><H2>The Floor Price of Trust</H2>
      {has ? (<><p><a href="./paper.pdf" download>Download the PDF</a></p><object data="./paper.pdf" type="application/pdf" className="w-full h-[70vh] border border-hair rounded-[14px]" aria-label="Paper PDF"><a href="./paper.pdf">Open the PDF</a></object></>)
        : (<p role="note">The final PDF is not published yet. It will appear here once exported.</p>)}
    </div>
  );
}

export default function App() {
  const [site, setSite] = useState<Site | null>(null);
  const [err, setErr] = useState(false);
  const [page, go] = useHash();
  useEffect(() => { loadSite().then(setSite).catch(() => setErr(true)); }, []);
  const body = useMemo(() => {
    if (err) return <p role="alert" className="pt-10">Could not load results data.</p>;
    if (!site) return <p className="pt-10">Loading results.</p>;
    return { findings: <Findings site={site} />, price: <PriceAttack site={site} />, techniques: <Techniques site={site} />, method: <Method site={site} />, paper: <Paper /> }[page];
  }, [site, err, page]);
  return (
    <>
      <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:left-2 focus:top-2 bg-lime p-2 z-30">Skip to content</a>
      <Nav page={page} go={go} />
      <main id="main" className="mx-auto max-w-5xl px-4">{body}</main>
      <footer className="mx-auto max-w-5xl px-4 pb-10 text-sm rule pt-4 mt-6"><p className="m-0">Floorprice, an Apart Research AI x Epistemics Sprint project by Kinnoski. Dana Reyes is fictional. Code and raw outputs are in the repository.</p></footer>
    </>
  );
}
