
import os

import edge_tts
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from fastapi.responses import Response

app = FastAPI(
    title="Indonesian TTS API",
    description="Text-to-Speech API untuk bahasa Indonesia",
    version="1.0.0",
)

# Untuk pengujian awal. Nanti batasi ke domain website Anda.
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


class TTSRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1200)
    voice: str = "id-ID-GadisNeural"


@app.get("/")
async def home():
    return {
        "status": "ok",
        "message": "Indonesian TTS API is running",
        "default_voice": "id-ID-GadisNeural",
    }


@app.post("/tts")
async def generate_speech(request: TTSRequest):
    text = request.text.strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="Text tidak boleh kosong",
        )

    allowed_voices = {
        "id-ID-GadisNeural",
        "id-ID-ArdiNeural",
    }

    if request.voice not in allowed_voices:
        raise HTTPException(
            status_code=400,
            detail="Voice tidak didukung",
        )

    try:
        communicator = edge_tts.Communicate(
            text,
            request.voice,
        )

        audio_data = bytearray()

        async for chunk in communicator.stream():
            if chunk["type"] == "audio":
                audio_data.extend(chunk["data"])

        if not audio_data:
            raise HTTPException(
                status_code=502,
                detail="Audio tidak berhasil dibuat",
            )

        return Response(
            content=bytes(audio_data),
            media_type="audio/mpeg",
            headers={"Cache-Control": "no-store"},
        )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Gagal membuat audio. Silakan coba kembali.",
        )

