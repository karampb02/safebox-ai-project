
import os
import uvicorn
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import AsyncGenerator

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000", # Assuming frontend might run on 3000 during development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for the frontend


# Get API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    LLM_PROVIDER = "gemini"
elif OPENAI_API_KEY:
    LLM_PROVIDER = "openai"
elif ANTHROPIC_API_KEY:
    LLM_PROVIDER = "anthropic"
else:
    LLM_PROVIDER = None

class URLAnalysisRequest(BaseModel):
    url: str

async def tier1_fast_check(url: str) -> tuple[bool, str]:
    """Basic Python function to check URL structure for common typosquatting or suspicious domains."""
    from urllib.parse import urlparse
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname

    if not hostname:
        return False, "Invalid URL structure (could not parse hostname)."

    # 1. Typosquatting/Homograph Attack
    common_brands = ["google.com", "microsoft.com", "apple.com", "amazon.com", "paypal.com"]
    for brand in common_brands:
        diff = sum(1 for a, b in zip(hostname, brand) if a != b)
        if len(hostname) == len(brand) and 0 < diff <= 2:
            return False, f"Potential typosquatting detected targeting brand domain '{brand}'."

    # 2. Suspicious TLDs
    suspicious_tlds = [".xyz", ".top", ".loan", ".bid", ".win", ".gq", ".cf", ".ga", ".ml", ".tk", ".pw", ".cn"]
    for tld in suspicious_tlds:
        if hostname.endswith(tld):
            return False, f"Suspicious Top-Level Domain ('{tld}') detected."

    # 3. IP address in hostname
    try:
        import ipaddress
        ipaddress.ip_address(hostname)
        return False, f"Raw IP address used as hostname ({hostname}), commonly used in phishing attacks."
    except ValueError:
        pass

    # 4. Excessive Subdomains
    if hostname.count('.') > 4:
        return False, f"Excessive subdomains detected ({hostname.count('.')} subdomains), indicating URL obfuscation."

    # 5. Punycode (homograph attacks)
    if "xn--" in hostname:
        return False, "Punycode (Internationalized Domain Name) detected, potential homograph attack."

    return True, "Passed initial structural security heuristics."

async def tier2_ai_analysis(url: str) -> AsyncGenerator[str, None]:
    """Integrates with an LLM via API to evaluate the URL for phishing patterns."""
    headers = {}
    payload = {}
    api_url = ""

    if not LLM_PROVIDER:
        yield "SafeBox AI Warning: No AI API Key detected in environment variables. Please set GEMINI_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY in your environment variables."
        return

    if LLM_PROVIDER == "gemini":
        if not GEMINI_API_KEY:
            yield "SafeBox AI Error: Gemini API key not configured."
            return
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent?alt=sse&key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"You are a cybersecurity expert. Analyze the following URL for potential phishing threats, credential harvesting red flags, brand impersonation, and overall safety. Provide a detailed report, highlighting any suspicious elements: {url}"
                        }
                    ]
                }
            ]
        }
    elif LLM_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            yield "SafeBox AI Error: OpenAI API key not configured."
            return
        api_url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "You are a cybersecurity expert. Analyze URLs for phishing, credential harvesting, and malicious intent. Provide a detailed safety report."},
                {"role": "user", "content": f"Analyze the following URL for potential phishing threats, credential harvesting red flags, and overall safety. Provide a detailed report, highlighting any suspicious elements: {url}"}
            ],
            "stream": True
        }
    elif LLM_PROVIDER == "anthropic":
        if not ANTHROPIC_API_KEY:
            yield "SafeBox AI Error: Anthropic API key not configured."
            return
        api_url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "claude-3-5-sonnet-20240620",
            "messages": [
                {"role": "user", "content": f"Analyze the following URL for potential phishing threats, credential harvesting red flags, and overall safety. Provide a detailed report, highlighting any suspicious elements: {url}"}
            ],
            "max_tokens": 1024,
            "stream": True
        }

    try:
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", api_url, headers=headers, json=payload, timeout=60.0) as response:
                if response.status_code != 200:
                    error_body = await response.aread()
                    yield f"SafeBox AI API Notice (HTTP {response.status_code}): {error_body.decode('utf-8', errors='ignore')[:250]}. Please ensure a valid GEMINI_API_KEY or OPENAI_API_KEY is configured."
                    return
                async for chunk in response.aiter_bytes():
                    if LLM_PROVIDER == "gemini":
                        try:
                            decoded_chunk = chunk.decode("utf-8")
                            for line in decoded_chunk.splitlines():
                                line = line.strip()
                                if line.startswith("data: "):
                                    json_str = line[6:].strip()
                                    if not json_str:
                                        continue
                                    import json
                                    data = json.loads(json_str)
                                    candidates = data.get("candidates", [])
                                    if candidates:
                                        parts = candidates[0].get("content", {}).get("parts", [])
                                        for p in parts:
                                            if "text" in p:
                                                yield p["text"]
                        except Exception:
                            continue
                    elif LLM_PROVIDER == "openai":
                        try:
                            decoded_chunk = chunk.decode("utf-8")
                            for line in decoded_chunk.splitlines():
                                if line.startswith("data: ") and line != "data: [DONE]":
                                    json_data = line[len("data: "):]
                                    import json
                                    data = json.loads(json_data)
                                    if "choices" in data and len(data["choices"]) > 0:
                                        content = data["choices"][0].get("delta", {}).get("content")
                                        if content:
                                            yield content
                        except Exception:
                            continue
                    elif LLM_PROVIDER == "anthropic":
                        try:
                            decoded_chunk = chunk.decode("utf-8")
                            for line in decoded_chunk.splitlines():
                                if line.startswith("data: "):
                                    json_data = line[len("data: "):]
                                    import json
                                    data = json.loads(json_data)
                                    if data.get("type") == "content_block_delta":
                                        yield data["delta"]["text"]
                        except Exception:
                            continue
    except Exception as e:
        yield f"SafeBox AI Connection Notice: Unable to reach AI service ({str(e)}). Please verify network and API key configuration."

@app.post("/analyze")
@app.post("/api/index")
async def analyze_url(request: URLAnalysisRequest):
    url = request.url

    # Tier 1: Fast Check
    is_safe, reason = await tier1_fast_check(url)
    if not is_safe:
        return StreamingResponse(
            content=iter([f"SafeBox Security Alert (Tier 1 Fast Check):\n\n• Analysis Result: Identified as potentially suspicious\n• Triggered Reason: {reason}\n• Recommendation: Proceed with extreme caution or avoid visiting this domain."]),
            media_type="text/event-stream"
        )

    # Tier 2: AI Analysis (streaming response)
    return StreamingResponse(tier2_ai_analysis(url), media_type="text/event-stream")

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
