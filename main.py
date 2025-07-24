from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import replicate
import os
import uuid

app = FastAPI()

# Serve static files
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For testing; change to your Shopify domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up Replicate client
replicate_client = replicate.Client(api_token=os.environ["REPLICATE_API_TOKEN"])

@app.post("/upload")
async def upload_image(
    plan: UploadFile = File(...),
    cabinet: str = Form(...),
    worktop: str = Form(...)
):
    # Save uploaded file
    filename = f"{uuid.uuid4()}.jpg"
    file_path = f"static/{filename}"
    with open(file_path, "wb") as f:
        f.write(await plan.read())

    # Open file for replicate input
    with open(file_path, "rb") as image_file:
        try:
            output = replicate.run(
                "lucataco/sdxl-controlnet:06d6fae3b75ab68a28cd2900afa6033166910dd09fd9751047043a5bbb4c184b",
                input={
                    "seed": 1234,
                    "image": image_file,
                    "prompt": f"kitchen with {cabinet} cabinets and {worktop} worktop, realistic, modern style",
                    "condition_scale": 0.6,
                    "negative_prompt": "low quality, bad sketch",
                    "num_inference_steps": 40
                }
            )

            # The output is typically a list of URLs
            if isinstance(output, list) and output:
                return JSONResponse({"image_url": output[0]})
            else:
                return JSONResponse({"error": "No image URL returned by AI."}, status_code=500)

        except replicate.exceptions.ReplicateError as e:
            return JSONResponse(
                status_code=500,
                content={"error": "AI render failed", "details": str(e)}
            )
