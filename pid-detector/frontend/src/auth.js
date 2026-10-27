const API = import.meta.env.VITE_API_URL || "http://localhost:8000";
const TOKEN_KEY = "lw_token";

async function post(path, body) {
  try {
    const res = await fetch(`${API}/auth${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const msg = typeof data.detail === "string" ? data.detail : "Check the details you entered.";
      return { ok: false, error: msg };
    }
    return { ok: true, ...data };
  } catch {
    return { ok: false, error: "Cannot reach the server. Is the backend running?" };
  }
}

function saveToken(r) {
  if (r.ok && r.token) localStorage.setItem(TOKEN_KEY, r.token);
  return r;
}

export const register = (username, email, password) =>
  post("/register", { username, email, password });
export const verifyEmail = async (email, code) => saveToken(await post("/verify", { email, code }));
export const login = async (identifier, password) =>
  saveToken(await post("/login", { identifier, password }));
export const googleLogin = async (credential) => saveToken(await post("/google", { credential }));
export const forgotPassword = (email) => post("/forgot", { email });
export const resetPassword = (email, code, password) =>
  post("/reset", { email, code, password });

export function logout() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem("lw_session");
}

export function isLoggedIn() {
  return !!localStorage.getItem(TOKEN_KEY);
}