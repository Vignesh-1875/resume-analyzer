# Colab smoke test (Runtime > T4 GPU)
```python
!pip -q install transformers accelerate pypdf sentence-transformers
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
name = "Qwen/Qwen2.5-1.5B-Instruct"
tok = AutoTokenizer.from_pretrained(name)
model = AutoModelForCausalLM.from_pretrained(name, device_map="auto", torch_dtype=torch.float16)
msgs = [{"role":"user","content":"List 5 skill gaps for a junior data scientist resume with only Excel."}]
ids = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt").to(model.device)
print(tok.decode(model.generate(ids, max_new_tokens=200)[0][ids.shape[1]:], skip_special_tokens=True))
```
To serve the Streamlit app from Colab: `!pip -q install streamlit pyngrok`, upload the `src/` folder + `app.py`,
set env vars (use Colab Secrets, not plain text), then tunnel port 8501 with ngrok.
