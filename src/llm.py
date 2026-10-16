"""Hugging Face instruction-tuned LLM wrapper (Qwen default; Gemma works via HF_MODEL)."""
import json
import re
import streamlit as st
from .config import get_secret

DEFAULT_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"  # use Qwen2.5-7B-Instruct on a bigger GPU


@st.cache_resource(show_spinner="Loading language model (first run downloads weights)...")
def load_model():
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    name = get_secret("HF_MODEL", DEFAULT_MODEL)
    token = get_secret("HF_TOKEN") or None
    tok = AutoTokenizer.from_pretrained(name, token=token)
    model = AutoModelForCausalLM.from_pretrained(
        name, token=token, device_map="auto",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32)
    return tok, model


def generate(system: str, user: str, max_new_tokens: int = 700) -> str:
    tok, model = load_model()
    msgs = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    inputs = tok.apply_chat_template(
        msgs,
        add_generation_prompt=True,
        return_tensors="pt",
        return_dict=True,
    )
    inputs = inputs.to(model.device)
    input_ids = inputs["input_ids"]
    out = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=0.4,
        top_p=0.9,
        pad_token_id=tok.eos_token_id,
    )
    return tok.decode(out[0][input_ids.shape[-1]:], skip_special_tokens=True).strip()


def generate_json(system: str, user: str, max_new_tokens: int = 900):
    """Ask for JSON; fall back to raw text if parsing fails."""
    raw = generate(system + " Respond with valid JSON only, no commentary.", user, max_new_tokens)
    m = re.search(r"[\[{].*[\]}]", raw, re.S)
    try:
        return json.loads(m.group(0)) if m else {"raw": raw}
    except json.JSONDecodeError:
        return {"raw": raw}
