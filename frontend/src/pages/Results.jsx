import React, { useMemo, useState } from "react";
import { Link, Navigate } from "react-router-dom";
import { inr } from "../api.js";
import { useMatch } from "../App.jsx";

function Card({ s, eligible }) {
  const passed = s.results.filter((r) => r.passed);
  const failed = s.results.filter((r) => !r.passed);
  return (
    <article className={"sch " + (eligible ? "ok" : s.near_miss ? "near" : "no")}>
      <header>
        <h3>{s.name}</h3>
        {eligible && <span className="tag good">Eligible</span>}
        {!eligible && s.near_miss && <span className="tag warn">1 criterion away</span>}
        {!eligible && !s.near_miss && <span className="tag bad">{s.failed_count} criteria missed</span>}
      </header>
      <p className="meta">{s.provider} | {s.level}</p>
      <div className="facts">
        <div><small>Benefit per year</small><strong>{inr(s.benefit_amount)}</strong></div>
        <div><small>Deadline</small><strong>{s.deadline}</strong></div>
      </div>
      {eligible ? (
        <div className="why">
          <strong>Why you qualify</strong>
          <ul>{passed.map((r, i) => <li key={i} className="pass">{r.message}</li>)}</ul>
        </div>
      ) : (
        <div className="why">
          <strong>{s.near_miss ? "What is missing" : "Why not"}</strong>
          <ul>{failed.map((r, i) => <li key={i} className="fail">{r.message}</li>)}</ul>
        </div>
      )}
      <footer>
        <Link className="btn small" to={`/scholarship/${s.id}`}>View details</Link>
        <a className="btn small ghost" href={s.official_link} target="_blank" rel="noreferrer">Official website</a>
      </footer>
    </article>
  );
}

export default function Results() {
  const { result, profile } = useMatch();
  const [tab, setTab] = useState("eligible");
  const [level, setLevel] = useState("");
  const [provider, setProvider] = useState("");
  const [sort, setSort] = useState("deadline");
  const [nearOnly, setNearOnly] = useState(false);

  const base = result ? (tab === "eligible" ? result.eligible : result.not_eligible) : [];
  const providers = useMemo(() => [...new Set((result ? [...result.eligible, ...result.not_eligible] : []).map((s) => s.provider))].sort(), [result]);

  const list = useMemo(() => {
    let l = base.filter((s) => (!level || s.level.split("/").includes(level)) && (!provider || s.provider === provider));
    if (tab === "not" && nearOnly) l = l.filter((s) => s.near_miss);
    const by = { deadline: (a, b) => a.deadline.localeCompare(b.deadline), amount: (a, b) => b.benefit_amount - a.benefit_amount, name: (a, b) => a.name.localeCompare(b.name) };
    return [...l].sort(by[sort]);
  }, [base, level, provider, sort, tab, nearOnly]);

  if (!result) return <Navigate to="/find" replace />;
  const c = result.counts;

  return (
    <section>
      <div className="summary">
        <h2>{c.eligible} scholarship{c.eligible === 1 ? "" : "s"} match your details</h2>
        <p className="muted">{c.near_miss} more are one criterion away. Checked {c.total} scholarships for a {profile.course_level} student in {profile.state}.</p>
        <Link className="btn small ghost" to="/find">Edit my details</Link>
      </div>

      <div className="tabs" role="tablist">
        <button role="tab" aria-selected={tab === "eligible"} className={tab === "eligible" ? "on" : ""} onClick={() => setTab("eligible")}>Eligible ({c.eligible})</button>
        <button role="tab" aria-selected={tab === "not"} className={tab === "not" ? "on" : ""} onClick={() => setTab("not")}>Not eligible ({c.not_eligible})</button>
      </div>

      <div className="filters">
        <label>Level
          <select value={level} onChange={(e) => setLevel(e.target.value)}>
            <option value="">All</option><option>UG</option><option>PG</option><option>Diploma</option>
          </select>
        </label>
        <label>Provider
          <select value={provider} onChange={(e) => setProvider(e.target.value)}>
            <option value="">All</option>
            {providers.map((p) => <option key={p}>{p}</option>)}
          </select>
        </label>
        <label>Sort by
          <select value={sort} onChange={(e) => setSort(e.target.value)}>
            <option value="deadline">Deadline (soonest)</option>
            <option value="amount">Amount (highest)</option>
            <option value="name">Name</option>
          </select>
        </label>
        {tab === "not" && <label className="inline"><input type="checkbox" checked={nearOnly} onChange={(e) => setNearOnly(e.target.checked)} /> Near-misses only</label>}
      </div>

      {list.length === 0 ? <p className="empty">No scholarships in this view. Try changing the filters.</p> : (
        <div className="cards">{list.map((s) => <Card key={s.id} s={s} eligible={tab === "eligible"} />)}</div>
      )}
    </section>
  );
}
