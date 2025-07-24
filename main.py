from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import replicate
import os
import uuid

app = FastAPI()

# Serve static files (e.g. images)
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Allow CORS for your Shopify frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your domain for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Replicate API token from environment variable
replicate_client = replicate.Client(api_token=os.environ["REPLICATE_API_TOKEN"])

@app.post("/upload")
async def upload_image(
    plan: UploadFile = File(...),
    cabinet: str = Form(...),
    worktop: str = Form(...)
):
    # Save the uploaded sketch
    filename = f"{uuid.uuid4()}.jpg"
    file_path = f"static/{filename}"
    with open(file_path, "wb") as f:
        f.write(await plan.read())

    # Use Replicate to generate render
    try:
        output_url = replicate.run(
            "lucataco/sdxl-controlnet:06d6fae3b75ab68a28cd2900afa6033166910dd09fd9751047043a5bbb4c184b",
            input={
                "seed": 1234,
                "image": f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/static/{filename}",
                "prompt": f"kitchen with {cabinet} cabinets and {worktop} worktop, realistic, modern style",
                "condition_scale": 0.6,
                "negative_prompt": "low quality, bad sketch",
                "num_inference_steps": 40
            }
        )

        return JSONResponse({"image_url": output_url})

    except replicate.exceptions.ReplicateError as e:
        return JSONResponse(
            status_code=500,
            content={"error": "AI render failed", "details": str(e)}
        )
