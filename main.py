from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import replicate
import uuid
import os

import base64

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or limit to your Shopify domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static folder (ensure it exists)
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Upload endpoint
@app.post("/upload")
async def upload_image(
    plan: UploadFile = File(...),
    worktop: str = Form(...),
    cabinet: str = Form(...)
):
    try:
        # Save uploaded file
        filename = f"{uuid.uuid4()}.jpg"
        file_path = f"static/{filename}"
        with open(file_path, "wb") as f:
            f.write(await plan.read())

        # Send to Replicate model
        output = replicate.run(
            "fofr/3d-kitchen-generator:735137ee7f6c4514ba84464cc36bc99a942a9c8f5e7b1a1910f8a2a4f3c0ad61",
            input={
                "image": open(file_path, "rb"),
                "cabinet": cabinet,
                "worktop": worktop
            }
        )

        return JSONResponse({"image_url": output})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
