from datetime import datetime, timezone
import streamlit as st
from pymongo import MongoClient, ASCENDING
from .config import get_secret


@st.cache_resource
def get_db():
    uri = get_secret("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI is not set (use .env or .streamlit/secrets.toml).")
    client = MongoClient(uri, tls=True, serverSelectionTimeoutMS=5000)
    db = client[get_secret("MONGODB_DB", "resume_analyzer")]
    db.users.create_index([("email", ASCENDING)], unique=True)
    db.analyses.create_index([("user_id", ASCENDING), ("created_at", ASCENDING)])
    return db


def save_analysis(user_id, kind: str, payload: dict):
    get_db().analyses.insert_one(
        {"user_id": user_id, "kind": kind, "payload": payload,
         "created_at": datetime.now(timezone.utc)})


def list_analyses(user_id, limit=20):
    return list(get_db().analyses.find({"user_id": user_id}).sort("created_at", -1).limit(limit))
