import os
import time
import json

# ── Provider: Gemini ──
def _try_gemini(prompt: str) -> str:
    import google.generativeai as genai
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(), override=True)
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key == "your_api_key_here":
        raise ValueError("No Gemini key")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    return response.text

# ── Provider: Groq (free tier – very generous) ──
def _try_groq(prompt: str) -> str:
    import requests
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(), override=True)
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key or api_key == "your_api_key_here":
        raise ValueError("No Groq key")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 1024
    }
    resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body, timeout=30)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def generate_response(prompt: str, max_retries: int = 2) -> str:
    """Try Gemini first, then Groq. Raises error if both fail."""
    providers = [
        ("Gemini", _try_gemini),
        ("Groq", _try_groq),
    ]
    
    last_error = None
    for name, fn in providers:
        for attempt in range(max_retries):
            try:
                return fn(prompt)
            except Exception as e:
                last_error = e
                error_str = str(e)
                if "429" in error_str or "ResourceExhausted" in error_str or "rate" in error_str.lower():
                    if attempt < max_retries - 1:
                        time.sleep(2 ** (attempt + 1))
                        continue
                break  # Non-retryable error, try next provider
    
    raise Exception(
        f"All LLM providers failed. Please set a valid GEMINI_API_KEY or GROQ_API_KEY in your .env file. "
        f"Get a free Groq key at https://console.groq.com — Last error: {last_error}"
    )

