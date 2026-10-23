const USERS_KEY = "lw_users";
const SESSION_KEY = "lw_session";

function getUsers() {
  try {
    return JSON.parse(localStorage.getItem(USERS_KEY)) || [];
  } catch {
    return [];
  }
}

function saveUsers(users) {
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

export function register(username, email, password) {
  username = username.trim();
  email = email.trim().toLowerCase();
  if (!username || !email || !password) return { ok: false, error: "Fill in all fields." };
  if (password.length < 6) return { ok: false, error: "Password must be at least 6 characters." };
  const users = getUsers();
  if (users.some((u) => u.username.toLowerCase() === username.toLowerCase()))
    return { ok: false, error: "That username is taken." };
  if (users.some((u) => u.email === email))
    return { ok: false, error: "That email is already registered." };
  users.push({ username, email, password });
  saveUsers(users);
  localStorage.setItem(SESSION_KEY, username);
  return { ok: true };
}

export function login(id, password) {
  id = id.trim().toLowerCase();
  const user = getUsers().find(
    (u) => u.username.toLowerCase() === id || u.email === id
  );
  if (!user || user.password !== password)
    return { ok: false, error: "Wrong username or password." };
  localStorage.setItem(SESSION_KEY, user.username);
  return { ok: true };
}

export function resetPassword(email, newPassword) {
  email = email.trim().toLowerCase();
  if (newPassword.length < 6) return { ok: false, error: "Password must be at least 6 characters." };
  const users = getUsers();
  const user = users.find((u) => u.email === email);
  if (!user) return { ok: false, error: "No account uses that email." };
  user.password = newPassword;
  saveUsers(users);
  return { ok: true };
}

export function logout() {
  localStorage.removeItem(SESSION_KEY);
}

export function isLoggedIn() {
  return !!localStorage.getItem(SESSION_KEY);
}