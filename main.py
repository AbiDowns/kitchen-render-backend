from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os

app = FastAPI()

# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://purplegranite.co.uk"],  # Or ["*"] for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ /upload route
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
