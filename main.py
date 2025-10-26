from fastapi import FastAPI, Request
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
        "servicetitan": r"servicetitan|st-cdn\.net|stapi|data-st-|stwidget|st-api|st-data",
        "housecallpro": r"housecallpro|hcp\.run|app\.housecallpro\.com|onlinerep\.app",
        "jobber": r"getjobber|jobber|clienthub\.app|jobber-api\.com|book\.getjobber\.com|api\.getjobber\.com",
    }

    try:
        response = requests.get(f"https://{domain}", timeout=8)
        html = response.text.lower()
        print("HTML length:", len(html))
    except Exception as e:
        print("Fetch error:", e)
        return JSONResponse(
            content={"domain": domain, "error": "fetch_failed"},
            status_code=502,
            media_type="application/json"
        )

    detected = {k: bool(re.search(v, html)) for k, v in patterns.items()}
    print("Detected:", detected)

    confidence = 0.9 if any(detected.values()) else 0.5
    result = {
        "domain": domain,
        **{f"uses_{k}": v for k, v in detected.items()},
        "confidence": confidence
    }

    print("Returning:", result)

    return JSONResponse(
        content=result,
        media_type="application/json"
    )

