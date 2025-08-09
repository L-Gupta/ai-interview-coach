from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse 
import os, httpx, io

router = APIRouter(tags=["Audio"])
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
DG_BASE = "https://api.deepgram.com/v1/speak"

@router.post("/tts")
async def tts_speak(payload: dict):
    if not DEEPGRAM_API_KEY:
        raise HTTPException(status_code=500, detail="Missing DEEPGRAM_API_KEY")
    
    text = (payload or {}).get("text", "").strip()
    model = (payload or {}).get("model", "aura-asteria-en")
    if not isinstance(text, str) or not text.strip():
        raise HTTPException(status_code=400, detail="Missing text")
    text = text.strip()

    url = f"{DG_BASE}?model={model}"
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }

    json_body = { "text": text }

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, headers=headers, json=json_body)
        if r.status_code != 200:
            detail = r.text[:500]
            print("[Deepgram TTS error]", r.status_code, detail)
            raise HTTPException(status_code=r.status_code, detail=detail)

    buf = io.BytesIO(r.content)
    return StreamingResponse(buf, media_type="audio/mpeg")
