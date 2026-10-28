import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, inr } from "../api.js";
import { useMatch } from "../App.jsx";

const LABEL = { income: "Annual family income", marks: "Previous-year marks", year: "Year of study", state: "State", category: "Category", gender: "Gender", course_level: "Course level", disability: "Disability", minority: "Minority status" };
const OP = { "<=": "at most", ">=": "at least", "==": "must be", in: "one of" };

export default function Detail() {
  const { id } = useParams();
  const { result } = useMatch();
  const [s, setS] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    api.get(id).then(setS).catch((e) => setErr(e.message));
  }, [id]);

  if (err) return <p className="err banner-err">{err}</p>;
  if (!s) return <p className="muted">Loading...</p>;

  const match = result ? [...result.eligible, ...result.not_eligible].find((x) => x.id === s.id) : null;
  const val = (c) => (c.field === "income" ? inr(c.value) : c.field === "marks" ? c.value + "%" : c.value.split(",").join(", "));

  return (
    <section className="card detail">
      <Link to={result ? "/results" : "/find"} className="back">Back</Link>
      <h2>{s.name}</h2>
      <p className="meta">{s.provider} | {s.level}</p>
      {match && (match.eligible
        ? <p className="tag good big">You are eligible</p>
        : <p className={"tag big " + (match.near_miss ? "warn" : "bad")}>Not eligible: {match.failed_count} criterion missed</p>)}
      <div className="facts">
        <div><small>Benefit per year</small><strong>{inr(s.benefit_amount)}</strong></div>
        <div><small>Deadline</small><strong>{s.deadline}</strong></div>
      </div>
      <p>{s.description}</p>

      <h3>Criteria</h3>
      <ul className="criteria">
        {s.criteria.map((c, i) => {
          const r = match ? match.results[i] : null;
          return (
            <li key={c.id} className={r ? (r.passed ? "pass" : "fail") : ""}>
              <span className="mark">{r ? (r.passed ? "✓" : "✗") : "•"}</span>
              <span><strong>{LABEL[c.field]}</strong> {OP[c.operator]} {val(c)}
                {r && <em className="reason"> {r.message}</em>}</span>
            </li>
          );
        })}
      </ul>

      <div className="trust">
        <strong>Source and verification</strong>
        <p>{s.is_sample ? "Sample record for the prototype. Not a real scheme." : "Criteria taken from the official source."}</p>
        <p className="muted">Source link: {s.source_link || "not recorded"} | Verified on: {s.verified_on || "not verified"}</p>
      </div>
      <a className="btn primary" href={s.official_link} target="_blank" rel="noreferrer">Open official website</a>
    </section>
  );
}
