import React, { useCallback, useEffect, useState } from "react";
import { api, inr } from "../api.js";

const FIELDS = {
  income: { kind: "numeric" }, marks: { kind: "numeric" }, year: { kind: "numeric" },
  state: { kind: "categorical" }, category: { kind: "categorical" }, gender: { kind: "categorical" }, course_level: { kind: "categorical" },
  disability: { kind: "boolean" }, minority: { kind: "boolean" },
};
const OPS = { numeric: ["<=", ">=", "=="], categorical: ["in", "=="], boolean: ["=="] };
const blank = () => ({ name: "", provider: "", level: "UG", official_link: "", deadline: "", benefit_amount: "", description: "", source_link: "", verified_on: "", is_sample: true, criteria: [{ field: "income", operator: "<=", value: "" }] });

export default function Admin() {
  const [token, setToken] = useState("");
  const [login, setLogin] = useState({ username: "", password: "" });
  const [msg, setMsg] = useState("");
  const [rows, setRows] = useState([]);
  const [edit, setEdit] = useState(null); // { id|null, data }

  const load = useCallback(() => api.list().then(setRows).catch((e) => setMsg(e.message)), []);
  useEffect(() => { if (token) load(); }, [token, load]);

  async function doLogin(e) {
    e.preventDefault();
    setMsg("");
    try { const r = await api.login(login.username, login.password); setToken(r.access_token); }
    catch (err) { setMsg(err.message); }
  }

  async function save(e) {
    e.preventDefault();
    setMsg("");
    const d = edit.data;
    const body = { ...d, benefit_amount: Number(d.benefit_amount), criteria: d.criteria.map(({ field, operator, value }) => ({ field, operator, value })) };
    try {
      if (edit.id) await api.update(edit.id, body, token); else await api.create(body, token);
      setEdit(null); load(); setMsg("Saved.");
    } catch (err) { setMsg(err.message); }
  }

  async function del(r) {
    if (!window.confirm(`Delete "${r.name}"?`)) return;
    try { await api.remove(r.id, token); load(); setMsg("Deleted."); } catch (err) { setMsg(err.message); }
  }

  const setD = (k) => (e) => setEdit({ ...edit, data: { ...edit.data, [k]: e.target.value } });
  const setC = (i, k, v) => {
    const criteria = edit.data.criteria.map((c, j) => {
      if (j !== i) return c;
      const n = { ...c, [k]: v };
      if (k === "field") { n.operator = OPS[FIELDS[v].kind][0]; n.value = ""; }
      return n;
    });
    setEdit({ ...edit, data: { ...edit.data, criteria } });
  };

  if (!token) {
    return (
      <section className="card form-card narrow">
        <h2>Admin login</h2>
        <p className="muted">For managing scholarships and their criteria.</p>
        <form onSubmit={doLogin}>
          <div className="field"><label htmlFor="u">Username</label><input id="u" value={login.username} onChange={(e) => setLogin({ ...login, username: e.target.value })} autoComplete="username" /></div>
          <div className="field"><label htmlFor="p">Password</label><input id="p" type="password" value={login.password} onChange={(e) => setLogin({ ...login, password: e.target.value })} autoComplete="current-password" /></div>
          {msg && <p className="err banner-err">{msg}</p>}
          <button className="btn primary big">Log in</button>
        </form>
      </section>
    );
  }

  if (edit) {
    const d = edit.data;
    return (
      <section className="card">
        <h2>{edit.id ? "Edit scholarship" : "Add scholarship"}</h2>
        <form onSubmit={save}>
          <div className="grid">
            <div className="field"><label>Name</label><input value={d.name} onChange={setD("name")} required /></div>
            <div className="field"><label>Provider</label><input value={d.provider} onChange={setD("provider")} required /></div>
            <div className="field"><label>Level (UG, PG, Diploma)</label><input value={d.level} onChange={setD("level")} required /></div>
            <div className="field"><label>Deadline (YYYY-MM-DD)</label><input value={d.deadline} onChange={setD("deadline")} placeholder="2027-03-31" required /></div>
            <div className="field"><label>Benefit per year (Rs)</label><input type="number" value={d.benefit_amount} onChange={setD("benefit_amount")} required /></div>
            <div className="field"><label>Official link</label><input value={d.official_link} onChange={setD("official_link")} required /></div>
            <div className="field"><label>Source link (where criteria were read)</label><input value={d.source_link} onChange={setD("source_link")} /></div>
            <div className="field"><label>Date verified</label><input value={d.verified_on} onChange={setD("verified_on")} placeholder="YYYY-MM-DD" /></div>
          </div>
          <div className="field"><label>Description</label><textarea rows="2" value={d.description} onChange={setD("description")} /></div>

          <h3>Criteria (all must pass)</h3>
          {d.criteria.map((c, i) => (
            <div className="crit-row" key={i}>
              <select value={c.field} onChange={(e) => setC(i, "field", e.target.value)}>{Object.keys(FIELDS).map((f) => <option key={f}>{f}</option>)}</select>
              <select value={c.operator} onChange={(e) => setC(i, "operator", e.target.value)}>{OPS[FIELDS[c.field].kind].map((o) => <option key={o}>{o}</option>)}</select>
              <input value={c.value} onChange={(e) => setC(i, "value", e.target.value)} placeholder={FIELDS[c.field].kind === "boolean" ? "yes or no" : c.operator === "in" ? "SC,ST" : "value"} required />
              <button type="button" className="btn small ghost" onClick={() => setEdit({ ...edit, data: { ...d, criteria: d.criteria.filter((_, j) => j !== i) } })}>Remove</button>
            </div>
          ))}
          <button type="button" className="btn small" onClick={() => setEdit({ ...edit, data: { ...d, criteria: [...d.criteria, { field: "income", operator: "<=", value: "" }] } })}>Add criterion</button>
          {msg && <p className="err banner-err">{msg}</p>}
          <div className="actions"><button className="btn primary">Save</button><button type="button" className="btn ghost" onClick={() => { setEdit(null); setMsg(""); }}>Cancel</button></div>
        </form>
      </section>
    );
  }

  return (
    <section>
      <div className="admin-head">
        <h2>Manage scholarships ({rows.length})</h2>
        <button className="btn primary" onClick={() => { setMsg(""); setEdit({ id: null, data: blank() }); }}>Add scholarship</button>
      </div>
      {msg && <p className="ok-msg">{msg}</p>}
      <div className="table-wrap">
        <table>
          <thead><tr><th>ID</th><th>Name</th><th>Provider</th><th>Level</th><th>Benefit</th><th>Deadline</th><th>Rules</th><th></th></tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td>{r.id}</td><td>{r.name}</td><td>{r.provider}</td><td>{r.level}</td><td>{inr(r.benefit_amount)}</td><td>{r.deadline}</td><td>{r.criteria.length}</td>
                <td className="row-actions">
                  <button className="btn small" onClick={() => { setMsg(""); setEdit({ id: r.id, data: { ...r, benefit_amount: String(r.benefit_amount) } }); }}>Edit</button>
                  <button className="btn small danger" onClick={() => del(r)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
