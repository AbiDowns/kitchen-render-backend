from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import replicate
import os
import uuid
import traceback

app = FastAPI()

# Serve static files (for uploaded images)
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Allow CORS (access from frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend domain for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Replicate client using API token from environment variable
replicate_client = replicate.Client(api_token=os.environ["REPLICATE_API_TOKEN"])

@app.post("/upload")
async def upload_image(
    plan: UploadFile = File(...),
    cabinet: str = Form(...),
    worktop: str = Form(...)
):
    try:
        # Save uploaded image
        filename = f"{uuid.uuid4()}.jpg"
        file_path = f"static/{filename}"
        with open(file_path, "wb") as f:
            f.write(await plan.read())

        # Public URL for the uploaded image
        image_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/static/{filename}"

        # Log the input for debugging
        print("🟡 Submitting to Replicate with:")
        print(f"Image: {image_url}")
        print(f"Prompt: kitchen with {cabinet} cabinets and {worktop} worktop, realistic, modern style")

        # Call Replicate API
        output = replicate.run(
            "lucataco/sdxl-controlnet:06d6fae3b75ab68a28cd2900afa6033166910dd09fd9751047043a5bbb4c184b",
            input={
                "seed": 1234,
                "image": image_url,
                "prompt": f"kitchen with {cabinet} cabinets and {worktop} worktop, realistic, modern style",
                "condition_scale": 0.6,
                "negative_prompt": "low quality, bad sketch",
                "num_inference_steps": 40
            }
        )

        # Return URL (single image or list)
        if isinstance(output, list) and len(output) > 0:
            return JSONResponse({"image_url": output[0]})
        else:
            return JSONResponse(status_code=500, content={"error": "No image returned from Replicate"})

    except Exception as e:
        print("❌ Exception occurred in /upload:")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": "AI render failed", "details": str(e)}
        )
