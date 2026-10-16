import re
from datetime import datetime, timezone
import bcrypt
from pymongo.errors import DuplicateKeyError
from .db import get_db

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_password(pw: str):
    if len(pw) < 8 or not re.search(r"[A-Za-z]", pw) or not re.search(r"\d", pw):
        return "Password must be 8+ characters with letters and digits."
    return None


def register(name: str, email: str, password: str):
    email = email.strip().lower()
    if not name.strip() or not EMAIL_RE.match(email):
        return False, "Enter a valid name and email."
    if (err := validate_password(password)):
        return False, err
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
    try:
        get_db().users.insert_one({"name": name.strip(), "email": email, "password": hashed,
                                   "created_at": datetime.now(timezone.utc)})
    except DuplicateKeyError:
        return False, "Email already registered."
    return True, "Registered. Please log in."


def login(email: str, password: str):
    user = get_db().users.find_one({"email": email.strip().lower()})
    # Same message for unknown user / wrong password (avoids account enumeration)
    if user and bcrypt.checkpw(password.encode(), user["password"]):
        return {"id": user["_id"], "name": user["name"], "email": user["email"]}
    return None
