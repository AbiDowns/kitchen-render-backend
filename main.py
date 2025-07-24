from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://purplegranite.co.uk"],  # ✅ Allow only your Shopify domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_image(
    plan: UploadFile = File(...),
    worktop: str = Form(...),
    cabinet: str = Form(...)
):
    filename = f"{uuid.uuid4()}.jpg"
    file_path = f"static/{filename}"
    os.makedirs("static", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(await plan.read())

    return JSONResponse({
        "image_url": "https://via.placeholder.com/800x400.png?text=Your+3D+Kitchen+Render"
    })

