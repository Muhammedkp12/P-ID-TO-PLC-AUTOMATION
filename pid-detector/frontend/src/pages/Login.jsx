import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login, register, resetPassword } from "../auth.js";
import AuthBackground from "../components/AuthBackground.jsx";
const TITLES = {
  login: "Log in or sign up in seconds",
  register: "Create your account",
  forgot: "Reset your password",
};

export default function Login({ mode = "login" }) {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [showEmailForm, setShowEmailForm] = useState(mode !== "login");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");
    setNotice("");
    let result;

    if (mode === "login") {
      result = login(username, password);
    } else if (mode === "register") {
      if (password !== confirm) return setError("Passwords do not match.");
      result = register(username, email, password);
    } else {
      if (password !== confirm) return setError("Passwords do not match.");
      result = resetPassword(email, password);
    }

    if (!result.ok) return setError(result.error);

    if (mode === "forgot") {
      setNotice("Password updated. Taking you to log in...");
      setTimeout(() => navigate("/login"), 1200);
      return;
    }
    navigate("/");
  };

  const showForm = mode !== "login" || showEmailForm;

  return (
    <div className="auth-page">
      <AuthBackground />
      <div className="auth-brand">Lineweight</div>

      <div className="auth-card">
        <h1>{TITLES[mode]}</h1>
        <p className="auth-sub">
          {mode === "login" && "Use your email or another service to continue with Lineweight (it's free!)"}
          {mode === "register" && "Fill in your details to get started."}
          {mode === "forgot" && "Enter your account email and choose a new password."}
        </p>

        {mode === "login" && !showEmailForm && (
          <>
            <button className="auth-btn" onClick={() => setShowEmailForm(true)}>
              Continue with username
            </button>
            <button
              className="auth-btn"
              onClick={() =>
                setNotice("Google sign-in needs a Google Client ID. Not set up yet.")
              }
            >
              Continue with Google
            </button>
            <button className="auth-btn" onClick={() => navigate("/register")}>
              Continue with email
            </button>
          </>
        )}

        {showForm && (
          <form onSubmit={handleSubmit} className="auth-form">
            {mode === "login" && (
              <input
                className="auth-input"
                placeholder="Username or email"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoFocus
              />
            )}

            {mode === "register" && (
              <>
                <input
                  className="auth-input"
                  placeholder="Username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
                <input
                  className="auth-input"
                  type="email"
                  placeholder="Email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </>
            )}

            {mode === "forgot" && (
              <input
                className="auth-input"
                type="email"
                placeholder="Account email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            )}

            <input
              className="auth-input"
              type={showPw ? "text" : "password"}
              placeholder={mode === "forgot" ? "New password" : "Password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />

            {mode !== "login" && (
              <input
                className="auth-input"
                type={showPw ? "text" : "password"}
                placeholder="Confirm password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
              />
            )}

            <label className="auth-check">
              <input type="checkbox" checked={showPw} onChange={(e) => setShowPw(e.target.checked)} />
              Show password
            </label>

            {error && <div className="auth-error">{error}</div>}
            {notice && <div className="auth-notice">{notice}</div>}

            <button type="submit" className="auth-btn auth-primary">
              {mode === "login" && "Log in"}
              {mode === "register" && "Sign up"}
              {mode === "forgot" && "Reset password"}
            </button>

            {mode === "login" && (
              <Link className="auth-link" to="/forgot-password">Forgot password?</Link>
            )}
          </form>
        )}

        {!showForm && notice && <div className="auth-notice">{notice}</div>}

        <div className="auth-switch">
          {mode === "login" && (
            <>New here? <Link to="/register">Create an account</Link></>
          )}
          {mode !== "login" && (
            <>Already have an account? <Link to="/login">Log in</Link></>
          )}
        </div>
      </div>
    </div>
  );
}