from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uuid
import os
import replicate

# Replace with your actual token
REPLICATE_API_TOKEN = r8_0RoLEtZ6Xd5LsPYIP5m9uHPwsCt14Pm2hsj7Q
replicate.Client(api_token=REPLICATE_API_TOKEN)

app = FastAPI()

# Serve uploaded static files (optional fallback)
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS for Shopify
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://purplegranite.co.uk"],
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
    # Save the uploaded sketch
    filename = f"{uuid.uuid4()}.jpg"
    file_path = f"static/{filename}"
    os.makedirs("static", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(await plan.read())

    # Call Replicate's sketch-to-image model
    output = replicate.run(
        "tstramer/t2i-adapter-sketch:1d2cd36d7a3d6f48a2026c0f8a3ebc87867b1cf8aa2ab167df92f06df2cbd32c",
        input={
            "image": open(file_path, "rb"),
            "prompt": f"3D render of a modern kitchen, {cabinet} cabinets, {worktop} worktop, natural lighting",
            "scale": 10,
            "seed": 42
        }
    )

    # Return the generated image URL
    return JSONResponse({
        "image_url": output[0]  # First image generated
    })

