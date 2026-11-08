import os
import subprocess
import tempfile
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image

app = FastAPI(title="GigProof OCR Server", version="1.0.0")

ALLOWED_MIMES = {"image/png", "image/jpeg", "image/jpg", "image/tiff", "image/bmp", "image/webp"}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB


@app.get("/health")
def health():
    return {"status": "ok", "engine": "tesseract"}


@app.post("/ocr")
async def ocr(
    file: UploadFile = File(...),
    lang: str = Form(default="eng"),
    psm: int = Form(default=6),
):
    if file.content_type not in ALLOWED_MIMES:
        raise HTTPException(status_code=400, detail=f"Unsupported MIME type: {file.content_type}")

    data = await file.read()
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 16 MB limit")

    # Validate it's actually an image
    try:
        img = Image.open(io.BytesIO(data))
        img.verify()
    except Exception:
        raise HTTPException(status_code=400, detail="File is not a valid image")

    suffix = os.path.splitext(file.filename or "upload.png")[1] or ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            ["tesseract", tmp_path, "stdout", "-l", lang, "--psm", str(psm)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=result.stderr.strip() or "Tesseract failed")
        return JSONResponse(
            {
                "text": result.stdout.strip(),
                "filename": file.filename,
                "lang": lang,
                "psm": psm,
            }
        )
    finally:
        os.unlink(tmp_path)


import io  # placed here to keep app.py tidy for the snippet above
