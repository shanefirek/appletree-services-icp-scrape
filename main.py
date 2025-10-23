from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests, re, os

app = FastAPI()

@app.post("/classify")
async def classify(request: Request):
    print("🚀 /classify hit")
    data = await request.json()
    domain = (data.get("domain") or data.get("Domain") or "").strip().lower()
    print("🌐 Domain received:", domain)

    if not domain:
        print("❌ No domain found")
        return JSONResponse({"error": "No domain received"}, status_code=400)

    patterns = {
        "servicetitan": r"servicetitan",
        "housecallpro": r"housecallpro|hcp\.run",
        "jobber": r"getjobber|jobber",
    }

    try:
        html = requests.get(f"https://{domain}", timeout=8).text.lower()
        print("📄 HTML fetched (length):", len(html))
    except Exception as e:
        print("❌ Fetch error:", e)
        return JSONResponse({"domain": domain, "error": "fetch_failed"})

    detected = {k: bool(re.search(v, html)) for k, v in patterns.items()}
    print("🔍 Detection results:", detected)

    confidence = 0.9 if any(detected.values()) else 0.5

    result = {
        "domain": domain,
        **{f"uses_{k}": v for k, v in detected.items()},
        "confidence": confidence
    }

    print("📤 Returning:", result)
    return JSONResponse(result)

