from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests, re, os

app = FastAPI()
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")

patterns = {
    "servicetitan": r"servicetitan",
    "housecallpro": r"housecallpro|hcp\.run",
    "jobber": r"getjobber|jobber",
}

@app.post("/classify")
async def classify(request: Request):
    data = await request.json()
    domain = data.get("domain")
    html = ""

    try:
        html = requests.get(f"https://{domain}", timeout=8).text.lower()
    except Exception:
        pass

    detected = {k: bool(re.search(v, html)) for k,v in patterns.items()}
    confidence = 0.9 if any(detected.values()) else 0.5

    return JSONResponse({
        "domain": domain,
        **{f"uses_{k}": v for k,v in detected.items()},
        "confidence": confidence
    })
