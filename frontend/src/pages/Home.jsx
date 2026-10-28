import React from "react";
import { Link } from "react-router-dom";

export default function Home() {
  return (
    <section className="hero">
      <h1>Find the scholarships you actually qualify for</h1>
      <p className="lead">Enter your details once. We check every criterion of every scholarship and tell you why you qualify, or which rule you miss.</p>
      <Link className="btn primary big" to="/find">Find Scholarships</Link>
      <div className="steps">
        <div className="step"><span>1</span><p>Fill a short form</p></div>
        <div className="step"><span>2</span><p>See matching scholarships with reasons</p></div>
        <div className="step"><span>3</span><p>Check near-misses and apply on the official site</p></div>
      </div>
    </section>
  );
}
