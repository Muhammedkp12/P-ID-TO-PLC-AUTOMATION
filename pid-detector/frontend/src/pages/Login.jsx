import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  login, register, verifyEmail, googleLogin, forgotPassword, resetPassword,
} from "../auth.js";

const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

const TITLES = {
  login: "Log in",
  register: "Create your account",
  forgot: "Reset your password",
};

export default function Login({ mode = "login" }) {
  const navigate = useNavigate();
  const googleBtn = useRef(null);
  const [step, setStep] = useState(1);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [code, setCode] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);

  const showGoogle = mode !== "forgot" && step === 1;

  // Real Google button
  useEffect(() => {
    if (!showGoogle || !CLIENT_ID) return;
    let tries = 0;
    const timer = setInterval(() => {
      tries += 1;
      if (window.google?.accounts?.id && googleBtn.current) {
        clearInterval(timer);
        window.google.accounts.id.initialize({
          client_id: CLIENT_ID,
          callback: async (resp) => {
            setError("");
            setBusy(true);
            const r = await googleLogin(resp.credential);
            setBusy(false);
            if (!r.ok) return setError(r.error);
            navigate("/");
          },
        });
        window.google.accounts.id.renderButton(googleBtn.current, {
          theme: "outline",
          size: "large",
          width: 380,
          text: mode === "register" ? "signup_with" : "continue_with",
        });
      } else if (tries > 50) {
        clearInterval(timer);
      }
    }, 100);
    return () => clearInterval(timer);
  }, [mode, showGoogle, navigate]);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setNotice("");
    setBusy(true);
    try {
      let r;
      if (mode === "login") {
        r = await login(username, password);
        if (r.ok) return navigate("/");
      } else if (mode === "register") {
        if (step === 1) {
          if (password !== confirm) return setError("Passwords do not match.");
          r = await register(username, email, password);
          if (r.ok) {
            setStep(2);
            setNotice(`We sent a 6-digit code to ${email}.`);
          }
        } else {
          r = await verifyEmail(email, code);
          if (r.ok) return navigate("/");
        }
      } else {
        if (step === 1) {
          r = await forgotPassword(email);
          if (r.ok) {
            setStep(2);
            setNotice("If that email has an account, we sent a 6-digit code.");
          }
        } else {
          if (password !== confirm) return setError("Passwords do not match.");
          r = await resetPassword(email, code, password);
          if (r.ok) {
            setNotice("Password changed. Taking you to log in...");
            setTimeout(() => navigate("/login"), 1200);
          }
        }
      }
      if (r && !r.ok) setError(r.error);
    } finally {
      setBusy(false);
    }
  };

  const pwType = showPw ? "text" : "password";
  const buttonText = {
    login: "Log in",
    register: step === 1 ? "Sign up" : "Verify email",
    forgot: step === 1 ? "Send code" : "Reset password",
  }[mode];

  return (
    <div className="auth-page">
      <header className="app-header">
        <div className="brand">
          <span className="brand-mark">Lineweight</span>
          <span className="brand-tag">P&amp;ID symbol detection</span>
        </div>
      </header>

      <div className="auth-card">
        <h1>{TITLES[mode]}</h1>

        <form onSubmit={submit} className="auth-form">
          {mode === "login" && (
            <>
              <input className="auth-input" placeholder="Username or email"
                value={username} onChange={(e) => setUsername(e.target.value)} autoFocus />
              <input className="auth-input" type={pwType} placeholder="Password"
                value={password} onChange={(e) => setPassword(e.target.value)} />
            </>
          )}

          {mode === "register" && step === 1 && (
            <>
              <input className="auth-input" placeholder="Username"
                value={username} onChange={(e) => setUsername(e.target.value)} autoFocus />
              <input className="auth-input" type="email" placeholder="Email"
                value={email} onChange={(e) => setEmail(e.target.value)} />
              <input className="auth-input" type={pwType} placeholder="Password (8+ characters)"
                value={password} onChange={(e) => setPassword(e.target.value)} />
              <input className="auth-input" type={pwType} placeholder="Confirm password"
                value={confirm} onChange={(e) => setConfirm(e.target.value)} />
            </>
          )}

          {mode === "forgot" && step === 1 && (
            <input className="auth-input" type="email" placeholder="Account email"
              value={email} onChange={(e) => setEmail(e.target.value)} autoFocus />
          )}

          {step === 2 && (
            <>
              <input className="auth-input" placeholder="6-digit code" inputMode="numeric"
                value={code} onChange={(e) => setCode(e.target.value)} autoFocus />
              {mode === "forgot" && (
                <>
                  <input className="auth-input" type={pwType} placeholder="New password (8+ characters)"
                    value={password} onChange={(e) => setPassword(e.target.value)} />
                  <input className="auth-input" type={pwType} placeholder="Confirm new password"
                    value={confirm} onChange={(e) => setConfirm(e.target.value)} />
                </>
              )}
            </>
          )}

          {(mode === "login" || (mode !== "login" && (step === 2 ? mode === "forgot" : mode === "register"))) && (
            <label className="auth-check">
              <input type="checkbox" checked={showPw} onChange={(e) => setShowPw(e.target.checked)} />
              Show password
            </label>
          )}

          {error && <div className="auth-error">{error}</div>}
          {notice && <div className="auth-notice">{notice}</div>}

          <button type="submit" className="auth-btn auth-primary" disabled={busy}>
            {busy ? "Please wait..." : buttonText}
          </button>

          {mode === "login" && (
            <Link className="auth-link" to="/forgot-password">Forgot password?</Link>
          )}
        </form>

        {showGoogle && (
          <>
            <div className="auth-divider"><span>or</span></div>
            {CLIENT_ID ? (
              <div ref={googleBtn} className="auth-google" />
            ) : (
              <div className="auth-error">Google sign-in is not configured (missing VITE_GOOGLE_CLIENT_ID).</div>
            )}
          </>
        )}

        <div className="auth-switch">
          {mode === "login" ? (
            <>New here? <Link to="/register">Create an account</Link></>
          ) : (
            <>Already have an account? <Link to="/login">Log in</Link></>
          )}
        </div>
      </div>
    </div>
  );
}