
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

async def tier1_fast_check(url: str) -> bool:
    """Basic Python function to check URL structure for common typosquatting or suspicious domains."""
    # This is a placeholder for a more robust check
    # In a real-world scenario, this would involve:
    # 1. Domain reputation lookups (e.g., Google Safe Browsing API, VirusTotal)
    # 2. Typosquatting detection (e.g., Levenshtein distance against popular domains)
    # 3. Heuristic analysis (e.g., excessive subdomains, unusual port numbers)
    # 4. Blacklist/Whitelist checks

    # Example: Basic checks for common phishing indicators
    from urllib.parse import urlparse
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname

    if not hostname:
        return False # Invalid URL structure

    # 1. Typosquatting/Homograph Attack (simplified check)
    # This is a very basic example. Real typosquatting detection is complex.
    common_brands = ["google.com", "microsoft.com", "apple.com", "amazon.com", "paypal.com"]
    for brand in common_brands:
        diff = sum(1 for a, b in zip(hostname, brand) if a != b)
        if len(hostname) == len(brand) and 0 < diff <= 2:
            print(f"[Tier 1] Potential typosquatting detected for {brand}")
            return False

    # 2. Suspicious TLDs (Top-Level Domains)
    suspicious_tlds = [".xyz", ".top", ".loan", ".bid", ".win", ".gq", ".cf", ".ga", ".ml", ".tk", ".pw", ".cn"]
    if any(hostname.endswith(tld) for tld in suspicious_tlds):
        print(f"[Tier 1] Suspicious TLD detected: {hostname}")
        return False

    # 3. IP address in hostname
    try:
        import ipaddress
        ipaddress.ip_address(hostname)
        print(f"[Tier 1] IP address used as hostname: {hostname}")
        return False # It's an IP address, often used in phishing
    except ValueError:
        pass # Not an IP address, proceed

    # 4. Excessive Subdomains (heuristic for obfuscation)
    if hostname.count('.') > 4: # e.g., very.long.subdomain.phishing.example.com
        print(f"[Tier 1] Excessive subdomains detected: {hostname}")
        return False

    # 5. Punycode (homograph attacks)
    if "xn--" in hostname:
        print(f"[Tier 1] Punycode detected: {hostname}")
        return False

    return True # Passed basic checks

async def tier2_ai_analysis(url: str) -> AsyncGenerator[str, None]:
    """Integrates with an LLM via API to evaluate the URL for phishing patterns."""
    headers = {}
    payload = {}
    api_url = ""

    if not LLM_PROVIDER:
        yield "SafeBox AI Warning: No AI API Key detected in environment variables. Please set GEMINI_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY in your .env file."
        return

    if LLM_PROVIDER == "gemini":
        if not GEMINI_API_KEY:
            raise HTTPException(status_code=500, detail="Gemini API key not configured.")
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:streamGenerateContent?alt=sse&key={GEMINI_API_KEY}"
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
            raise HTTPException(status_code=500, detail="OpenAI API key not configured.")
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
            raise HTTPException(status_code=500, detail="Anthropic API key not configured.")
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

    async with httpx.AsyncClient() as client:
        try:
            async with client.stream("POST", api_url, headers=headers, json=payload, timeout=60.0) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    # Process chunks based on LLM provider
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
                        # OpenAI sends JSON objects, need to parse and extract content
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
                            # Handle incomplete JSON chunks
                            continue
                    elif LLM_PROVIDER == "anthropic":
                        # Anthropic sends JSON objects, need to parse and extract content
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

        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"LLM API request failed: {e}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"LLM API returned an error: {e.response.text}")

@app.post("/analyze")
async def analyze_url(request: URLAnalysisRequest):
    url = request.url

    # Tier 1: Fast Check
    if not await tier1_fast_check(url):
        return StreamingResponse(content=iter(["SafeBox Web: Initial fast check identified this URL as potentially suspicious. Proceed with caution or avoid."]), media_type="text/event-stream")

    # Tier 2: AI Analysis (streaming response)
    return StreamingResponse(tier2_ai_analysis(url), media_type="text/event-stream")

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
