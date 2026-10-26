import os, re, time, secrets, sqlite3, smtplib
from email.message import EmailMessage
from pathlib import Path

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as g_requests

load_dotenv()
router = APIRouter(prefix="/auth", tags=["auth"])

DB = Path(__file__).resolve().parent.parent / "users.db"
JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE, email TEXT UNIQUE, pw_hash BLOB,
            verified INTEGER DEFAULT 0, code TEXT, code_exp REAL)"""
    )
    return conn


def pw_bytes(p: str) -> bytes:
    return p.encode()[:72]


def check_password_rules(p: str):
    if len(p) < 8:
        raise HTTPException(400, "Password must be at least 8 characters.")


def make_token(username: str) -> str:
    return jwt.encode(
        {"sub": username, "exp": time.time() + 7 * 86400}, JWT_SECRET, algorithm="HS256"
    )


def send_email(to: str, subject: str, body: str):
    host, user, pw = os.getenv("SMTP_HOST"), os.getenv("SMTP_USER"), os.getenv("SMTP_PASS")
    if not (host and user and pw):
        raise HTTPException(500, "Email sending is not configured on the server.")
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = user, to, subject
    msg.set_content(body)
    try:
        with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587"))) as s:
            s.starttls()
            s.login(user, pw)
            s.send_message(msg)
    except Exception:
        raise HTTPException(500, "Could not send the email. Check the SMTP settings.")


def send_code(conn, email: str, subject: str):
    code = f"{secrets.randbelow(1000000):06d}"
    conn.execute(
        "UPDATE users SET code=?, code_exp=? WHERE email=?",
        (code, time.time() + 600, email),
    )
    send_email(email, subject, f"Your Lineweight code is {code}. It expires in 10 minutes.")


def code_ok(user, code: str) -> bool:
    return bool(
        user and user["code"] and user["code"] == code.strip() and user["code_exp"] > time.time()
    )


class RegisterIn(BaseModel):
    username: str
    email: str
    password: str


class VerifyIn(BaseModel):
    email: str
    code: str


class LoginIn(BaseModel):
    identifier: str
    password: str


class GoogleIn(BaseModel):
    credential: str


class EmailIn(BaseModel):
    email: str


class ResetIn(BaseModel):
    email: str
    code: str
    password: str


@router.post("/register")
def register(body: RegisterIn):
    username, email = body.username.strip(), body.email.strip().lower()
    if not username or not EMAIL_RE.match(email):
        raise HTTPException(400, "Enter a username and a valid email.")
    check_password_rules(body.password)
    with db() as conn:
        existing = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if existing and existing["verified"]:
            raise HTTPException(400, "That email is already registered.")
        if existing:
            conn.execute("DELETE FROM users WHERE id=?", (existing["id"],))
        if conn.execute(
            "SELECT 1 FROM users WHERE lower(username)=lower(?)", (username,)
        ).fetchone():
            raise HTTPException(400, "That username is taken.")
        pw = bcrypt.hashpw(pw_bytes(body.password), bcrypt.gensalt())
        conn.execute(
            "INSERT INTO users(username,email,pw_hash) VALUES(?,?,?)", (username, email, pw)
        )
        send_code(conn, email, "Verify your Lineweight account")
    return {"ok": True}


@router.post("/verify")
def verify(body: VerifyIn):
    email = body.email.strip().lower()
    with db() as conn:
        u = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if not code_ok(u, body.code):
            raise HTTPException(400, "Wrong or expired code.")
        conn.execute("UPDATE users SET verified=1, code=NULL, code_exp=NULL WHERE id=?", (u["id"],))
        return {"token": make_token(u["username"])}


@router.post("/login")
def login(body: LoginIn):
    ident = body.identifier.strip().lower()
    with db() as conn:
        u = conn.execute(
            "SELECT * FROM users WHERE lower(username)=? OR email=?", (ident, ident)
        ).fetchone()
    if not u or not u["pw_hash"] or not bcrypt.checkpw(pw_bytes(body.password), u["pw_hash"]):
        raise HTTPException(401, "Wrong username or password.")
    if not u["verified"]:
        raise HTTPException(403, "Verify your email first. Create the account again to get a new code.")
    return {"token": make_token(u["username"])}


@router.post("/google")
def google(body: GoogleIn):
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(500, "Google sign-in is not configured on the server.")
    try:
        info = id_token.verify_oauth2_token(body.credential, g_requests.Request(), GOOGLE_CLIENT_ID)
    except ValueError as e:
        print("GOOGLE VERIFY ERROR:", e)
        raise HTTPException(401, "Google sign-in failed.")
    if not info.get("email_verified"):
        raise HTTPException(401, "Your Google email is not verified.")
    email = info["email"].lower()
    with db() as conn:
        u = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if u:
            conn.execute(
                "UPDATE users SET pw_hash=CASE WHEN verified=0 THEN NULL ELSE pw_hash END, verified=1 WHERE id=?",
                (u["id"],),
            )
            username = u["username"]
        else:
            base = (info.get("name") or email.split("@")[0]).strip()
            username, n = base, 1
            while conn.execute(
                "SELECT 1 FROM users WHERE lower(username)=lower(?)", (username,)
            ).fetchone():
                n += 1
                username = f"{base}{n}"
            conn.execute(
                "INSERT INTO users(username,email,verified) VALUES(?,?,1)", (username, email)
            )
    return {"token": make_token(username)}


@router.post("/forgot")
def forgot(body: EmailIn):
    email = body.email.strip().lower()
    with db() as conn:
        u = conn.execute("SELECT * FROM users WHERE email=? AND verified=1", (email,)).fetchone()
        if u:
            send_code(conn, email, "Reset your Lineweight password")
    return {"ok": True}  # same answer whether or not the email exists


@router.post("/reset")
def reset(body: ResetIn):
    email = body.email.strip().lower()
    check_password_rules(body.password)
    with db() as conn:
        u = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if not code_ok(u, body.code):
            raise HTTPException(400, "Wrong or expired code.")
        pw = bcrypt.hashpw(pw_bytes(body.password), bcrypt.gensalt())
        conn.execute(
            "UPDATE users SET pw_hash=?, code=NULL, code_exp=NULL WHERE id=?", (pw, u["id"])
        )
    return {"ok": True}