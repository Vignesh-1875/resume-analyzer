"""Secrets are read from environment variables or Streamlit secrets - never hardcoded."""
import os
from dotenv import load_dotenv

load_dotenv()


def get_secret(key: str, default=None):
    value = os.getenv(key)
    if value:
        return value
    try:
        import streamlit as st
        return st.secrets.get(key, default)
    except Exception:
        return default
