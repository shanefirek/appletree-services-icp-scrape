from fastapi import FastAPI
from pydantic import BaseModel
import requests, re, os
from fastapi.responses import JSONResponse

class DomainInput(BaseModel):
    domain: str

app = FastAPI()

@app.post("/classify")
async def classify(data: DomainInput):
    domain = data.domain
    html = ""
    patterns = {
        "servicetitan": r"servicetitan",
        "housecallpro": r"housecallpro|hcp\.run",
        "jobber": r"getjobber|jobber",
    }

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
