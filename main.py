from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
import re

app = FastAPI()

class DomainRequest(BaseModel):
    domain: str

@app.post("/classify")
async def classify(data: DomainRequest):
    domain = data.domain.strip().lower()
    print("Domain received:", domain)

    if not domain:
        return JSONResponse(
            content={"error": "No domain received"},
            status_code=400,
            media_type="application/json"
        )

    patterns = {
        "servicetitan": r"(servicetitan\.com|cdn\.servicetitan\.com|st-cdn\.net|stwidget-[a-z0-9]|st-api\.servicetitan)",
        "housecallpro": r"(housecallpro\.com|hcp\.run|app\.housecallpro\.com|onlinerep\.app)",
        "jobber": r"(getjobber\.com|clienthub\.app|book\.getjobber\.com|jobber-api\.com|api\.getjobber\.com)",
    }

    ignore_patterns = [
        r"stackpath\.bootstrapcdn\.com",
        r"st\.js",
        r"data-st-[a-z0-9\-]+"
    ]

    try:
        headers = {"User-Agent": "Mozilla/5.0 (SignalDetector/1.0)"}
        response = requests.get(f"https://{domain}", headers=headers, timeout=10)
        html = response.text.lower()
        print(f"Fetched {len(html)} chars from {domain}")
    
    except Exception as e:
        print("Fetch error:", e)
        return JSONResponse(
            content={"domain": domain, "error": "fetch_failed"},
            status_code=502,
            media_type="application/json"
        )

    for bad in ignore_patterns:
        html = re.sub(bad, "", html)

    detected = {}
    matches = {}

    for vendor, pattern in patterns.items():
        match = re.search(pattern, html)
        if match:
            detected[vendor] = True
            matches[vendor] = match.group(0)
        else:
            detected[vendor] = False

    print("Detected:", detected)
    if len(matches) > 0:
        print("Matched substrings:", matches)

    confidence = 0.95 if any(detected.values()) else 0.5
    result = {
        "domain": domain,
        **{f"uses_{vendor}": detected[vendor] for vendor in patterns},
        "confidence": confidence,
        "matches": matches
    }

    return JSONResponse(content=result, media_type="application/json")

