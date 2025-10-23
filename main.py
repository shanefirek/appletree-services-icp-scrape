from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/classify")
async def classify(request: Request):
    body = await request.body()        # raw bytes
    print("🧾 RAW BODY:", body)         # see exactly what Clay sends
    try:
        data = await request.json()
    except Exception as e:
        print("❌ JSON parse error:", e)
        data = {}

    print("📦 Parsed JSON:", data)
    domain = data.get("domain") or data.get("Domain")
    return JSONResponse({"echo_domain": domain})
