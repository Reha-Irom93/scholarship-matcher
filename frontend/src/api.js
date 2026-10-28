const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, { method = "GET", body, token } = {}) {
  const headers = {};
  if (body) headers["Content-Type"] = "application/json";
  if (token) headers["Authorization"] = "Bearer " + token;
  let res;
  try {
    res = await fetch(BASE + path, { method, headers, body: body ? JSON.stringify(body) : undefined });
  } catch {
    throw new Error("Cannot reach the server. Is the backend running?");
  }
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    let msg = data.detail;
    if (Array.isArray(msg)) msg = msg.map((e) => `${(e.loc || []).slice(1).join(".")}: ${e.msg}`).join("; ");
    throw new Error(msg || `Request failed (${res.status})`);
  }
  return data;
}

export const api = {
  match: (profile) => request("/match", { method: "POST", body: profile }),
  list: () => request("/scholarships"),
  get: (id) => request(`/scholarships/${id}`),
  login: (username, password) => request("/admin/login", { method: "POST", body: { username, password } }),
  create: (b, token) => request("/scholarships", { method: "POST", body: b, token }),
  update: (id, b, token) => request(`/scholarships/${id}`, { method: "PUT", body: b, token }),
  remove: (id, token) => request(`/scholarships/${id}`, { method: "DELETE", token }),
};

export const inr = (n) => "Rs " + Number(n).toLocaleString("en-IN");
