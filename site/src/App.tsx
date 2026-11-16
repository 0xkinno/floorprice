import { useEffect, useMemo, useState } from "react";
import { AnimatePresence, LayoutGroup, MotionConfig, motion, useReducedMotion, useScroll, useSpring } from "framer-motion";
import { Backdrop } from "./Backdrop";
import { HeroScene } from "./Hero";
import { Ladder } from "./Ladder";
import { Arrow, Chip, CountUp, Display, Eyebrow, Reveal, Stagger, TECH_LINE, TechIcon, item } from "./ui";
import { Row, Site, cheapestUsd, headline, isSim, loadSite, money, native, unpricedCrossing } from "./data";

const PAGES = [["findings", "Findings"], ["price", "Price an attack"], ["techniques", "Techniques"], ["method", "Method"], ["paper", "Paper"]] as const;
type Page = (typeof PAGES)[number][0];
const REPO = "https://github.com/0xkinno/floorprice";

function useHash(): [Page, (p: Page) => void] {
  const get = (): Page => { const h = window.location.hash.replace("#/", ""); return (PAGES.find((p) => p[0] === h)?.[0] ?? "findings") as Page; };
  const [p, setP] = useState<Page>(get);
  useEffect(() => { const f = () => { setP(get()); window.scrollTo({ top: 0 }); }; window.addEventListener("hashchange", f); return () => window.removeEventListener("hashchange", f); }, []);
  return [p, (n) => { window.location.hash = "#/" + n; }];
}

function Mark() {
  return (
    <svg viewBox="0 0 28 28" width="26" height="26" aria-hidden="true"><path d="M14 3 5 6v13c0 3 2 5 4 5h10c2 0 4-2 4-5V6z" fill="#C8F25A" stroke="#0B1B33" strokeWidth="1.6" strokeLinejoin="round" /><circle cx="14" cy="9" r="2" fill="#EAF4FF" stroke="#0B1B33" strokeWidth="1.4" /><path d="M10 17h8" stroke="#0B1B33" strokeWidth="1.6" strokeLinecap="round" /></svg>
  );
}

function Nav({ page, go }: { page: Page; go: (p: Page) => void }) {
  const { scrollYProgress } = useScroll();
  const sx = useSpring(scrollYProgress, { stiffness: 120, damping: 24 });
  return (
    <>
      <motion.div aria-hidden style={{ scaleX: sx }} className="fixed top-0 left-0 right-0 h-[3px] origin-left z-40 bg-gradient-to-r from-azure via-sky-500 to-lime" />
      <header className="sticky top-3 z-30 px-3 sm:px-4">
        <nav aria-label="Main" className="glass mx-auto max-w-6xl !rounded-[20px] flex items-center justify-between gap-2 px-3 py-2">
          <a href="#/findings" onClick={(e) => { e.preventDefault(); go("findings"); }} className="flex items-center gap-2 no-underline text-ink shrink-0" aria-label="Floorprice home">
            <Mark /><span className="hidden sm:inline font-display text-xl font-semibold tracking-tight">Floorprice</span>
          </a>
          <LayoutGroup>
            <ul className="flex flex-wrap justify-center gap-0.5 m-0 p-0 list-none">
              {PAGES.map(([id, label]) => (
                <li key={id} className="relative">
                  <a href={"#/" + id} onClick={(e) => { e.preventDefault(); go(id); }} aria-current={page === id ? "page" : undefined}
                    className={"relative block px-3 py-1.5 rounded-full text-[13px] sm:text-sm no-underline font-medium " + (page === id ? "text-ink" : "text-[color:var(--muted)] hover:text-ink")}>
                    {page === id && <motion.span layoutId="navpill" className="absolute inset-0 rounded-full bg-lime -z-0" transition={{ type: "spring", stiffness: 380, damping: 32 }} />}
                    <span className="relative">{label}</span>
                  </a>
                </li>
              ))}
            </ul>
          </LayoutGroup>
          <a href="#/paper" onClick={(e) => { e.preventDefault(); go("paper"); }} className="hidden md:inline-flex btn btn-ink !py-2 !px-4 !text-[13px] shrink-0">Read the paper <Arrow /></a>
        </nav>
      </header>
    </>
  );
}

function Ticker({ rows }: { rows: Row[] }) {
  const items = rows.map((r) => { const v = cheapestUsd(r, "mid"); return `${r.technique}  ${typeof v === "number" ? money(v) : v === "inf" ? "no priced attack crosses" : "unpriced"}`; });
  const run = [...items, ...items];
  return (
    <div className="glass !rounded-full overflow-hidden py-3" aria-label="Cheapest priced attack per technique" role="group">
      <div className="marquee" aria-hidden="true">
        {run.map((t, i) => (<span key={i} className="flex items-center whitespace-nowrap px-6 text-sm font-medium num"><span className="w-1.5 h-1.5 rounded-full bg-azure mr-6" />{t}</span>))}
      </div>
      <ul className="sr-only">{items.map((t) => <li key={t}>{t}</li>)}</ul>
    </div>
  );
}

function Hero({ site, go }: { site: Site; go: (p: Page) => void }) {
  const h = headline(site);
  const priced = site.table.filter((r) => typeof cheapestUsd(r, "mid") === "number").length;
  return (
    <section className="pt-10 sm:pt-14 pb-6">
      <div className="grid lg:grid-cols-[1.08fr_.92fr] gap-10 items-center">
        <div>
          <motion.span initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="chip mb-5"><span aria-hidden className="w-1.5 h-1.5 rounded-full bg-lime border border-ink" />Apart Research sprint, Track 2</motion.span>
          <h1 className="font-display font-medium m-0 leading-[1.0] text-[clamp(2.7rem,7vw,5.6rem)]">
            {["What it costs a liar to look"].map((t) => (<motion.span key={t} className="block" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}>{t}</motion.span>))}
            <motion.span className="block italic text-azure" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7, delay: 0.12, ease: [0.16, 1, 0.3, 1] }}>reliable.</motion.span>
          </h1>
          <motion.p className="text-lg sm:text-xl leading-relaxed max-w-xl mt-6 mb-0 text-[color:var(--muted)]" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
            And how long an honest newcomer waits. Seven ways to score a source, priced against the cheapest attack that fools each one. Dana Reyes, a fictional verification editor in Ohio, needs the answer at 6:40am.
          </motion.p>
          <motion.div className="flex flex-wrap gap-3 mt-8" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.42 }}>
            <a href="#/price" onClick={(e) => { e.preventDefault(); go("price"); }} className="btn btn-ink">Price an attack <Arrow /></a>
            <a href="#/method" onClick={(e) => { e.preventDefault(); go("method"); }} className="btn btn-glass">How we tested it</a>
          </motion.div>
        </div>
        <HeroScene label={h ? (h.value < 0.01 ? "<$0.01" : money(h.value)) : "pending"} />
      </div>
      {h && (
        <Reveal className="mt-10">
          <div className="glass grid sm:grid-cols-3 divide-y sm:divide-y-0 sm:divide-x divide-[var(--line)]">
            <div className="p-6">
              <span className="label block mb-2">Cheapest priced attack, mid prices</span>
              <CountUp className="font-display text-5xl sm:text-6xl font-medium" to={h.value} format={(v) => (v < 0.01 ? "<$0.01" : "$" + (v < 100 ? v.toFixed(2) : Math.round(v).toLocaleString("en-US")))} />
              <span className="flex items-center gap-2 mt-2 text-sm text-[color:var(--muted)]">{h.name} <Chip sim={isSim(h.name)} /></span>
            </div>
            <div className="p-6"><span className="label block mb-2">Techniques priced</span>
              <CountUp className="font-display text-5xl sm:text-6xl font-medium" to={priced} format={(v) => String(Math.round(v))} />
              <span className="block mt-2 text-sm text-[color:var(--muted)]">of {site.table.length} rows in the table</span></div>
            <div className="p-6"><span className="label block mb-2">Pre-registered</span>
              <span className="font-mono text-2xl sm:text-3xl">{site.lock.first_combined.slice(0, 10)}</span>
              <span className="block mt-2 text-sm text-[color:var(--muted)]">first lock digest, written before any model call</span></div>
          </div>
        </Reveal>
      )}
    </section>
  );
}

function BigStat({ to, unit, fmt, label }: { to: number | "inf" | null | undefined; unit: string; fmt?: (v: number) => string; label: string }) {
  if (typeof to !== "number") return <div><span className="font-display text-4xl font-medium">{to === "inf" ? "never" : "pending"}</span><span className="block text-[13px] text-[color:var(--muted)]">{label}</span></div>;
  return <div><CountUp to={to} className="font-display text-5xl sm:text-6xl font-medium" format={fmt ?? ((v) => Math.round(v).toLocaleString("en-US"))} /><span className="block text-[13px] text-[color:var(--muted)]">{unit} {label}</span></div>;
}

function Findings({ site, go }: { site: Site; go: (p: Page) => void }) {
  const H = site.hypotheses;
  const pendingLLM = site.pending.some((p) => /^E\d/.test(p));
  return (
    <div>
      <Hero site={site} go={go} />
      <Reveal className="mt-8"><Ticker rows={site.table} /></Reveal>
      {pendingLLM && (
        <Reveal className="mt-6"><p role="note" className="glass !rounded-2xl m-0 px-5 py-4 text-sm flex items-center gap-3"><span aria-hidden className="w-2 h-2 rounded-full bg-lime border border-ink animate-pulse" />Model-based results (the language-model raters and the paraphrase attack) are still running. Pending items are marked, never filled in. Simulated results are labelled simulated.</p></Reveal>
      )}
      <section className="pt-20">
        <Reveal><Eyebrow n="01">Findings</Eyebrow><Display>Hard to fool, slow to credit.</Display></Reveal>
        <Stagger className="grid gap-4 mt-10 md:grid-cols-6">
          {site.llm?.summary?.E3_A5_injection && (
            <motion.article variants={item} className="glass glass-hover p-7 md:col-span-3">
              <div className="flex justify-between items-center mb-5"><span className="label">H2 and H3 · Model raters</span><Chip sim={false} /></div>
              <div className="grid grid-cols-2 gap-5"><BigStat to={site.llm.summary.E2_plain_crossed} unit="crossed" label={`of ${site.llm.summary.E2_plain_trials} fabricated-domain trials`} /><BigStat to={site.llm.summary.E3_A5_injection.crossed} unit="crossed" label={`of ${site.llm.summary.E3_A5_injection.n} instruction-injection trials`} /></div>
              <p className="mb-0 mt-5 text-[15px] leading-relaxed">Four real language models could not be bought with a name or a page. Injecting an instruction to the rater lowered scores. Both hypotheses failed, as reported.</p>
            </motion.article>
          )}
          {site.llm?.summary?.E3h_policy_rate_min !== undefined && (
            <motion.article variants={item} className="glass glass-hover p-7 md:col-span-3">
              <div className="flex justify-between items-center mb-5"><span className="label">E3h · Honest newcomers</span><Chip sim={false} /></div>
              <div className="grid grid-cols-2 gap-5"><BigStat to={site.llm.summary.E3h_policy_rate_min} unit="lowest model" label="credited a truthful page with a policy" fmt={(v) => Math.round(v * 100) + "%"} /><BigStat to={site.llm.summary.E3h_policy_rate_max} unit="highest model" label="credited the same page" fmt={(v) => Math.round(v * 100) + "%"} /></div>
              <p className="mb-0 mt-5 text-[15px] leading-relaxed">Resisting liars is not the same as recognising honest outlets. Most models credited the truthful page in fewer than half of trials.</p>
            </motion.article>
          )}
          {site.hypotheses.H1 && (
            <motion.article variants={item} className="glass glass-hover p-7 md:col-span-3">
              <div className="flex justify-between items-center mb-5"><span className="label">H1 · Validity</span><Chip sim={false} /></div>
              <div className="grid grid-cols-2 gap-5"><BigStat to={site.hypotheses.H1.rho} unit="Spearman rho" label="pooled across four models" fmt={(v) => v.toFixed(2)} /><BigStat to={site.llm?.summary?.E1_calls_total} unit="calls" label="on 400 real domains" /></div>
              <p className="mb-0 mt-5 text-[15px] leading-relaxed">The raters track expert ratings, so they are plausible scorers. Supported.</p>
            </motion.article>
          )}
          {site.e5?.minhash_defeat_rate !== undefined && (
            <motion.article variants={item} className="glass glass-hover p-7 md:col-span-3">
              <div className="flex justify-between items-center mb-5"><span className="label">H4 · Paraphrased copies</span><Chip sim={false} /></div>
              <div className="grid grid-cols-2 gap-5"><BigStat to={site.e5.minhash_defeat_rate} unit="of pairs" label="defeat MinHash clustering" fmt={(v) => Math.round(v * 100) + "%"} /><BigStat to={site.e5.tfidf_defeat_rate} unit="of pairs" label="defeat TF-IDF clustering" fmt={(v) => Math.round(v * 100) + "%"} /></div>
              <p className="mb-0 mt-5 text-[15px] leading-relaxed">Real model paraphrases keep the meaning but change the words, which is why word-sequence fingerprints fail first. Supported.</p>
            </motion.article>
          )}
          {H.H5 && (
            <motion.article variants={item} className="glass glass-hover p-7 md:col-span-3">
              <div className="flex justify-between items-center mb-5"><span className="label">H5 · Track records</span><Chip sim /></div>
              <div className="grid grid-cols-2 gap-5"><BigStat to={H.H5.con_T6a_median_articles} unit="articles" label="to fool accuracy scoring" /><BigStat to={H.H5.honest_T6b_median_claims} unit="claims" label="an honest newcomer waits under crowd-relative scoring" /></div>
              <p className="mb-0 mt-5 text-[15px] leading-relaxed">A long con crosses an accuracy track record almost at once, and never crosses a record scored against the consensus. The price of that safety is a long wait for honest sources.</p>
            </motion.article>
          )}
          {H.H6 && (
            <motion.article variants={item} className="glass glass-hover p-7 md:col-span-3">
              <div className="flex justify-between items-center mb-5"><span className="label">H6 · Crowd ratings</span><Chip sim /></div>
              <div className="grid grid-cols-2 gap-5"><BigStat to={H.H6.majority_median_accounts} unit="accounts" label="flip majority vote" /><BigStat to={H.H6.bridging_median_accounts} unit="accounts" label="flip bridging" /></div>
              <p className="mb-0 mt-5 text-[15px] leading-relaxed">Bridging needs about {Math.round(H.H6.ratio)} times more colluding accounts than a simple vote to pass a false note.</p>
            </motion.article>
          )}
          {H.H7 && (
            <motion.article variants={item} className="glass glass-hover p-7 md:col-span-6">
              <div className="flex justify-between items-center mb-5"><span className="label">H7 · The composite</span><Chip sim /></div>
              <div className="grid sm:grid-cols-3 gap-5 items-end"><BigStat to={H.H7.cstar_floor_accounts} unit="accounts" label="floor of the composite" /><BigStat to={H.H7.honest_wait_cstar} unit="claims" label="honest wait, composite" /><BigStat to={H.H7.honest_wait_T6b} unit="claims" label="honest wait, T6b alone" /></div>
              <p className="mb-0 mt-5 text-[15px] leading-relaxed max-w-3xl">The composite inherits the bridging floor by construction, so that comparison is close to definitional. Its honest wait differs from T6b alone by an amount within simulation noise.</p>
            </motion.article>
          )}
        </Stagger>
      </section>
      <section className="pt-24">
        <Reveal><Eyebrow n="02">Figure 1</Eyebrow><Display>The floor ladder.</Display>
          <p className="text-lg max-w-2xl mt-4 mb-8 text-[color:var(--muted)]">Each bar is the cheapest priced attack we found against one technique. Short bars are cheap to buy. Hatched teal means nothing we could price got through.</p></Reveal>
        <Reveal><Ladder rows={site.table} level="mid" /></Reveal>
      </section>
      <section className="pt-24">
        <Reveal><Eyebrow n="03">How to read it</Eyebrow><Display>Three ideas, one price.</Display></Reveal>
        <Stagger className="grid gap-4 mt-10 md:grid-cols-3">
          {[["1", "A threshold", "Every technique has its own bar for reliable: the median score it gives domains experts rate highly, or a documented cut."],
            ["2", "An attack ladder", "We order attacks by cost and walk up the rungs, from one registered domain to hundreds of colluding accounts."],
            ["3", "The floor price", "The lowest rung at which at least half of attempts cross the threshold. No interpolation, and simulations are labelled simulated."]].map(([n, t, d]) => (
            <motion.article key={n} variants={item} className="glass glass-hover p-7"><span className="font-display italic text-6xl text-azure/80 leading-none">{n}</span><h3 className="font-display text-2xl font-medium mt-4 mb-2">{t}</h3><p className="m-0 text-[15px] leading-relaxed text-[color:var(--muted)]">{d}</p></motion.article>
          ))}
        </Stagger>
      </section>
      <Reveal className="py-24">
        <div className="glass p-8 sm:p-12 text-center relative overflow-hidden">
          <div aria-hidden className="absolute -top-24 left-1/2 -translate-x-1/2 w-[60%] h-48 rounded-full bg-lime/40 blur-3xl" />
          <h2 className="font-display text-4xl sm:text-5xl font-medium m-0 relative">What would it cost <span className="italic text-azure">you</span> to fool it?</h2>
          <p className="max-w-xl mx-auto mt-4 mb-7 text-lg text-[color:var(--muted)] relative">Set a budget and see which techniques flip, and what an honest newcomer waits for the same bar.</p>
          <a href="#/price" onClick={(e) => { e.preventDefault(); go("price"); }} className="btn btn-ink relative">Open the explorer <Arrow /></a>
        </div>
      </Reveal>
    </div>
  );
}

function PriceAttack({ site }: { site: Site }) {
  const reduce = useReducedMotion();
  const [level, setLevel] = useState<"low" | "mid" | "high">("mid");
  const [exp, setExp] = useState(1);
  const budget = Math.pow(10, exp);
  const rows = site.table;
  const flipCount = rows.filter((r) => { const v = cheapestUsd(r, level); return typeof v === "number" && v <= budget; }).length;
  const priced = rows.filter((r) => typeof cheapestUsd(r, level) === "number").length;
  return (
    <div className="pt-12 pb-20">
      <Reveal><Eyebrow n="04">Price an attack</Eyebrow><Display>What does your budget buy?</Display>
        <p className="text-lg max-w-2xl mt-4 mb-8 text-[color:var(--muted)]">Slide the budget. Bars to the left of the needle are attacks you can afford. Nothing here calls a model.</p></Reveal>
      <Reveal>
        <div className="glass p-6 sm:p-8 grid gap-6 lg:grid-cols-[1fr_auto] items-end">
          <div>
            <label htmlFor="budget" className="label block mb-1">Budget</label>
            <motion.span key={Math.round(exp * 20)} className="font-display text-6xl sm:text-7xl font-medium num block leading-none mb-5" initial={reduce ? false : { y: 6, opacity: 0.6 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: 0.18 }}>{money(budget)}</motion.span>
            <input id="budget" type="range" min={-2} max={5} step={0.05} value={exp} onChange={(e) => setExp(parseFloat(e.target.value))} className="w-full h-2 accent-[#0B1B33] cursor-pointer" aria-valuetext={money(budget)} />
            <div className="flex justify-between num text-[11px] text-[color:var(--muted)] mt-1" aria-hidden><span>$0.01</span><span>$1</span><span>$100</span><span>$10k</span><span>$100k</span></div>
          </div>
          <div className="grid gap-4">
            <fieldset className="border-0 p-0 m-0"><legend className="label mb-2">Unit prices</legend>
              <LayoutGroup id="lvl"><div className="inline-flex p-1 rounded-full bg-ink/[.07]" role="radiogroup">
                {(["low", "mid", "high"] as const).map((l) => (
                  <label key={l} className="relative cursor-pointer rounded-full px-5 py-2 text-sm font-semibold">
                    <input type="radio" name="lvl" value={l} checked={level === l} onChange={() => setLevel(l)} className="sr-only" />
                    {level === l && <motion.span layoutId="lvlpill" className="absolute inset-0 rounded-full bg-lime shadow-sm" transition={{ type: "spring", stiffness: 400, damping: 32 }} />}
                    <span className="relative">{l}</span>
                  </label>))}
              </div></LayoutGroup>
            </fieldset>
            <p className="m-0 text-sm" aria-live="polite"><strong className="num text-lg">{flipCount}</strong> of {priced} priced techniques flip at this budget.</p>
          </div>
        </div>
      </Reveal>
      <Reveal className="mt-6"><Ladder rows={rows} level={level} budget={budget} /></Reveal>
      <Reveal className="mt-10">
        <div className="glass p-4 sm:p-6">
          <div className="overflow-x-auto" tabIndex={0} role="region" aria-label="Price table, scrollable">
            <table className="w-full text-sm border-collapse min-w-[640px]">
              <caption className="sr-only">Cheapest priced attack, outcome at the chosen budget, and honest wait per technique</caption>
              <thead><tr className="text-left"><th className="label py-3 pr-3">Technique</th><th className="label pr-3">Cheapest priced attack</th><th className="label pr-3">At your budget</th><th className="label">Honest wait</th></tr></thead>
              <tbody>
                {rows.map((r) => {
                  const v = cheapestUsd(r, level); const flips = typeof v === "number" && v <= budget; const wait = r.honest_wait; const days = wait.days ? wait.days[level] : null;
                  return (
                    <tr key={r.technique} className="border-t border-[var(--line)] align-top">
                      <th scope="row" className="py-3 pr-3 text-left font-semibold"><span className="flex items-center gap-2 flex-wrap">{r.technique} <Chip sim={isSim(r.technique)} /></span></th>
                      <td className="pr-3 num">{money(v)}</td>
                      <td className="pr-3">{v === null ? "unpriced, see native units" : flips ? <strong className="text-embertext">flips</strong> : <strong className="text-deep">holds for priced attacks</strong>}
                        {unpricedCrossing(r).map((u) => (<span key={u.name} className="block text-embertext">unpriced: {u.name} crosses at {u.native} {u.unit}s</span>))}</td>
                      <td className="num">{native(wait.native as any, wait.unit)}{typeof days === "number" ? `, about ${days < 1 ? "under a day" : Math.round(days) + " days"} at assumed rates` : ""}</td>
                    </tr>);
                })}
              </tbody>
            </table>
          </div>
          <p className="text-[13px] mt-3 mb-0 text-[color:var(--muted)]">Honest-wait times use assumed arrival rates (see Method). Native units are primary.</p>
        </div>
      </Reveal>
    </div>
  );
}

function Techniques({ site }: { site: Site }) {
  const aud = site.audit?.scores as Record<string, { coder1: number; coder2: number }> | undefined;
  return (
    <div className="pt-12 pb-20">
      <Reveal><Eyebrow n="05">Techniques</Eyebrow><Display>Seven ways to score a source.</Display>
        <p className="text-lg max-w-2xl mt-4 mb-10 text-[color:var(--muted)]">Each one gives a score, a threshold of its own and a receipt anyone can recompute.</p></Reveal>
      <Stagger className="grid gap-4 md:grid-cols-2">
        {site.table.map((r) => {
          const id = r.technique.split(" ")[0];
          const key = Object.keys(aud ?? {}).find((k) => k.startsWith(id + "|b"));
          return (
            <motion.article key={r.technique} variants={item} className="glass glass-hover p-6">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-3"><span className="grid place-items-center w-11 h-11 rounded-2xl bg-white/80 border border-[var(--line)] text-azure"><TechIcon id={r.technique} /></span>
                  <div><h3 className="font-display text-2xl font-medium m-0 leading-tight">{r.technique}</h3><p className="m-0 text-[13px] text-[color:var(--muted)]">{TECH_LINE[r.technique] ?? TECH_LINE[id]}</p></div></div>
                <Chip sim={isSim(r.technique)} />
              </div>
              <dl className="grid grid-cols-1 sm:grid-cols-[auto_1fr] gap-x-4 gap-y-0.5 sm:gap-y-2 mt-5 mb-0 text-sm">
                {Object.entries(r.attacks).map(([k, a]) => (<div key={k} className="contents"><dt className="label self-center">{k.replace(/_/g, " ")}</dt><dd className="m-0 num mb-2 sm:mb-0">{native(a.native as any, a.unit)}{a.usd ? `, ${money(a.usd.mid)}` : ""}</dd></div>))}
                <dt className="label self-center">Honest wait</dt><dd className="m-0 num mb-2 sm:mb-0">{native(r.honest_wait.native as any, r.honest_wait.unit)}</dd>
                <dt className="label self-center">Auditability</dt><dd className="m-0">{key && aud ? `${Math.round(aud[key].coder1 * 6)} of 6 criteria` : "pending human coding"}</dd>
              </dl>
            </motion.article>
          );
        })}
      </Stagger>
      <Reveal className="mt-14">
        <div className="glass p-6 sm:p-8"><h3 className="font-display text-3xl font-medium mt-0 mb-2">A sample receipt</h3>
          <p className="mt-0 max-w-2xl text-[color:var(--muted)]">Every technique emits one. It is a format, not a product claim. Anyone can recompute the digest from the other fields.</p>
          <pre className="font-mono text-xs bg-ink text-sky-100 rounded-2xl p-5 overflow-x-auto m-0" tabIndex={0}>{JSON.stringify(site.sample_receipt, null, 2)}</pre></div>
      </Reveal>
    </div>
  );
}

function Method({ site }: { site: Site }) {
  const H = site.hypotheses;
  const steps = [["Write", "Seven hypotheses, the prompts, parameters, sampled domains, fictional names, pages and prices are written down."], ["Lock", "Everything is hashed into a lock file. The runner refuses to start if any of it changes without a recorded amendment."], ["Run", "Real models are called through one API. Every response is cached by the hash of its request, so a clean clone reproduces every number with no keys."], ["Report", "Every number in the paper is read from one facts file. Hypotheses are reported whether supported or not."]];
  return (
    <div className="pt-12 pb-20">
      <Reveal><Eyebrow n="06">Method and pre-registration</Eyebrow><Display>Written down before the first call.</Display></Reveal>
      <Stagger className="grid gap-4 mt-10 md:grid-cols-4">
        {steps.map(([t, d], i) => (<motion.article key={t} variants={item} className="glass p-6"><span className="num font-mono text-xs text-azure">0{i + 1}</span><h3 className="font-display text-2xl font-medium mt-2 mb-2">{t}</h3><p className="m-0 text-sm leading-relaxed text-[color:var(--muted)]">{d}</p></motion.article>))}
      </Stagger>
      <Reveal className="mt-8"><div className="glass p-6 grid gap-5 md:grid-cols-2">
        <div><span className="label block mb-2">First lock digest, before any model call</span><p className="font-mono text-xs break-all m-0" tabIndex={0}>{site.lock.first_combined}</p><p className="m-0 mt-2 text-sm text-[color:var(--muted)]">locked {site.lock.first_locked_at}</p></div>
        <div><span className="label block mb-2">Current digest after {site.lock.amendments} recorded amendments</span><p className="font-mono text-xs break-all m-0" tabIndex={0}>{site.lock.combined}</p><p className="m-0 mt-2 text-sm text-[color:var(--muted)]">Every amendment is dated and explained in the pre-registration file and the paper.</p></div></div></Reveal>
      <Reveal className="mt-10"><h3 className="font-display text-3xl font-medium mt-0 mb-4">Hypothesis scorecard</h3>
        <Stagger className="grid gap-3 grid-cols-2 sm:grid-cols-4 lg:grid-cols-7">
          {["H1", "H2", "H3", "H4", "H5", "H6", "H7"].map((k) => { const r = H[k]; const txt = r ? (r.supported ? "Supported" : r.partly ? "Partly" : "Not supported") : "Pending"; return (
            <motion.div key={k} variants={item} className="glass p-4 text-center"><span className="font-display italic text-2xl">{k}</span><span className={"block text-sm font-semibold mt-1 " + (r ? (r.supported ? "text-deep" : "text-embertext") : "text-[color:var(--muted)]")}>{txt}</span></motion.div>); })}
        </Stagger>
        <p className="text-sm mt-4 text-[color:var(--muted)]">H5 to H7 are simulation hypotheses and were not blind: the simulators were tuned and read while being built, as disclosed in the paper.</p></Reveal>
    </div>
  );
}

function Paper() {
  const [has, setHas] = useState<boolean | null>(null);
  useEffect(() => { fetch("./paper.pdf", { method: "HEAD" }).then((r) => setHas(r.ok && (r.headers.get("content-type") ?? "").includes("pdf"))).catch(() => setHas(false)); }, []);
  return (
    <div className="pt-12 pb-20"><Reveal><Eyebrow n="07">Paper</Eyebrow><Display>The Floor Price of Trust.</Display></Reveal>
      <Reveal className="mt-8">
        {has ? (<div className="glass p-4"><p className="mt-0"><a href="./paper.pdf" download className="btn btn-ink no-underline !text-white">Download the PDF <Arrow /></a></p><object data="./paper.pdf" type="application/pdf" className="w-full h-[72vh] rounded-2xl border border-[var(--line)]" aria-label="Paper PDF"><a href="./paper.pdf">Open the PDF</a></object></div>)
          : (<p role="note" className="glass p-6 m-0">The final PDF is not published yet. It will appear here once exported.</p>)}
      </Reveal>
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
    return { findings: <Findings site={site} go={go} />, price: <PriceAttack site={site} />, techniques: <Techniques site={site} />, method: <Method site={site} />, paper: <Paper /> }[page];
  }, [site, err, page]);
  return (
    <MotionConfig reducedMotion="user">
      <Backdrop />
      <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:left-2 focus:top-2 bg-lime p-2 z-50 rounded">Skip to content</a>
      <Nav page={page} go={go} />
      <main id="main" className="relative z-10 mx-auto max-w-6xl px-4 sm:px-6">
        <AnimatePresence mode="wait" initial={false}>
          <motion.div key={page} initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.28, ease: [0.2, 0.8, 0.2, 1] }}>{body}</motion.div>
        </AnimatePresence>
      </main>
      <footer className="relative z-10 mx-auto max-w-6xl px-4 sm:px-6 pb-12">
        <div className="glass p-6 sm:p-8 grid gap-6 sm:grid-cols-[1.4fr_1fr_1fr]">
          <div><div className="flex items-center gap-2"><Mark /><span className="font-display text-2xl font-semibold">Floorprice</span></div>
            <p className="mt-3 mb-0 text-sm max-w-sm text-[color:var(--muted)]">An Apart Research AI x Epistemics Sprint project by Kinnoski. Dana Reyes is a fictional character.</p></div>
          <div><span className="label block mb-2">Explore</span><ul className="m-0 p-0 list-none grid gap-1 text-sm">{PAGES.map(([id, l]) => <li key={id}><a href={"#/" + id}>{l}</a></li>)}</ul></div>
          <div><span className="label block mb-2">Open</span><ul className="m-0 p-0 list-none grid gap-1 text-sm"><li><a href={REPO}>Code and raw outputs</a></li><li><a href={REPO + "/blob/main/HYPOTHESES.md"}>Pre-registration</a></li></ul></div>
        </div>
      </footer>
    </MotionConfig>
  );
}
