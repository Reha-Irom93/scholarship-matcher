import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api.js";
import { useMatch } from "../App.jsx";

export const STATES = ["Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Delhi","Goa","Gujarat","Haryana","Himachal Pradesh","Jammu and Kashmir","Jharkhand","Karnataka","Kerala","Madhya Pradesh","Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura","Uttar Pradesh","Uttarakhand","West Bengal"];

const EMPTY = { state: "", category: "", gender: "", income: "", course_level: "", year: "", marks: "", disability: false, minority: false };

const Field = ({ id, label, children, hint, errors }) => (
  <div className={"field" + (errors[id] ? " has-error" : "")}>
    <label htmlFor={id}>{label}</label>
    {children}
    {hint && <small>{hint}</small>}
    {errors[id] && <span className="err">{errors[id]}</span>}
  </div>
);

export default function Find() {
  const nav = useNavigate();
  const { profile, setProfile, setResult } = useMatch();
  const [f, setF] = useState(profile ? { ...profile } : EMPTY);
  const [errors, setErrors] = useState({});
  const [busy, setBusy] = useState(false);
  const [serverError, setServerError] = useState("");

  const set = (k) => (e) => setF({ ...f, [k]: e.target.type === "checkbox" ? e.target.checked : e.target.value });

  function validate() {
    const e = {};
    if (!f.state) e.state = "Choose your state";
    if (!f.category) e.category = "Choose your category";
    if (!f.gender) e.gender = "Choose your gender";
    if (f.income === "" || Number(f.income) < 0 || Number.isNaN(Number(f.income))) e.income = "Enter annual family income (0 or more)";
    if (!f.course_level) e.course_level = "Choose your course level";
    if (!f.year) e.year = "Choose your year";
    if (f.marks === "" || Number(f.marks) < 0 || Number(f.marks) > 100) e.marks = "Enter marks between 0 and 100";
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function submit(ev) {
    ev.preventDefault();
    setServerError("");
    if (!validate()) return;
    const body = { ...f, income: Number(f.income), year: Number(f.year), marks: Number(f.marks) };
    setBusy(true);
    try {
      const res = await api.match(body);
      setProfile(f);
      setResult(res);
      nav("/results");
    } catch (err) {
      setServerError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="card form-card">
      <h2>Your details</h2>
      <p className="muted">Used only to find matches. Nothing is stored.</p>
      <form onSubmit={submit} noValidate>
        <div className="grid">
          <Field errors={errors} id="state" label="State">
            <select id="state" value={f.state} onChange={set("state")}>
              <option value="">Select state</option>
              {STATES.map((s) => <option key={s}>{s}</option>)}
            </select>
          </Field>
          <Field errors={errors} id="category" label="Category">
            <select id="category" value={f.category} onChange={set("category")}>
              <option value="">Select category</option>
              {["General", "OBC", "SC", "ST", "EWS"].map((s) => <option key={s}>{s}</option>)}
            </select>
          </Field>
          <Field errors={errors} id="gender" label="Gender">
            <select id="gender" value={f.gender} onChange={set("gender")}>
              <option value="">Select gender</option>
              {["Male", "Female", "Other"].map((s) => <option key={s}>{s}</option>)}
            </select>
          </Field>
          <Field errors={errors} id="income" label="Annual family income (Rs)" hint="For example 250000">
            <input id="income" type="text" inputMode="numeric" autoComplete="off" value={f.income} onChange={(e) => setF({ ...f, income: e.target.value.replace(/[^0-9]/g, "") })} />
          </Field>
          <Field errors={errors} id="course_level" label="Course level">
            <select id="course_level" value={f.course_level} onChange={set("course_level")}>
              <option value="">Select level</option>
              {["UG", "PG", "Diploma"].map((s) => <option key={s}>{s}</option>)}
            </select>
          </Field>
          <Field errors={errors} id="year" label="Year of study">
            <select id="year" value={f.year} onChange={set("year")}>
              <option value="">Select year</option>
              {[1, 2, 3, 4, 5, 6].map((s) => <option key={s}>{s}</option>)}
            </select>
          </Field>
          <Field errors={errors} id="marks" label="Previous-year marks (%)">
            <input id="marks" type="text" inputMode="decimal" autoComplete="off" value={f.marks} onChange={(e) => setF({ ...f, marks: e.target.value.replace(/[^0-9.]/g, "") })} />
          </Field>
        </div>
        <div className="checks">
          <label><input type="checkbox" checked={f.disability} onChange={set("disability")} /> Person with disability</label>
          <label><input type="checkbox" checked={f.minority} onChange={set("minority")} /> Belongs to a minority community</label>
        </div>
        {serverError && <p className="err banner-err">{serverError}</p>}
        <button className="btn primary big" disabled={busy}>{busy ? "Searching..." : "Find Scholarships"}</button>
      </form>
    </section>
  );
}
