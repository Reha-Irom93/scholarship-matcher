import React, { createContext, useContext, useState } from "react";
import { Link, NavLink, Route, Routes } from "react-router-dom";
import Home from "./pages/Home.jsx";
import Find from "./pages/Find.jsx";
import Results from "./pages/Results.jsx";
import Detail from "./pages/Detail.jsx";
import Admin from "./pages/Admin.jsx";

// Student details live only in memory (this context). Nothing is saved to the browser or the server.
const MatchContext = createContext(null);
export const useMatch = () => useContext(MatchContext);

export default function App() {
  const [profile, setProfile] = useState(null);
  const [result, setResult] = useState(null);
  return (
    <MatchContext.Provider value={{ profile, setProfile, result, setResult }}>
      <header className="topbar">
        <Link to="/" className="brand">Scholarship Matcher</Link>
        <nav>
          <NavLink to="/find">Find Scholarships</NavLink>
          <NavLink to="/admin">Admin</NavLink>
        </nav>
      </header>
      <div className="sample-banner" role="note">
        Prototype with <strong>sample data</strong>: the scholarships shown are illustrative, not real schemes.
        Always confirm on the official website before applying.
      </div>
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/find" element={<Find />} />
          <Route path="/results" element={<Results />} />
          <Route path="/scholarship/:id" element={<Detail />} />
          <Route path="/admin" element={<Admin />} />
        </Routes>
      </main>
      <footer className="footer">Advisory only. Your details are used for this search and are not stored.</footer>
    </MatchContext.Provider>
  );
}
