from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uuid
import os
import replicate

# Initialize FastAPI app
app = FastAPI()

# Allow frontend to talk to backend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://purplegranite.co.uk"],  # Update with your live store URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Make sure static directory exists
os.makedirs("static", exist_ok=True)

# Mount static file folder (for future use)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Get Replicate token from env
replicate_client = replicate.Client(api_token=os.environ["REPLICATE_API_TOKEN"])

# Upload endpoint
@app.post("/upload")
async def upload_image(
    plan: UploadFile = File(...),
    cabinet: str = Form(...),
    worktop: str = Form(...)
):
    try:
        # Save uploaded image to local file
        filename = f"{uuid.uuid4()}.jpg"
        file_path = f"static/{filename}"
        with open(file_path, "wb") as f:
            f.write(await plan.read())

        # Call Replicate model (update with actual model)
        model_output = replicate_client.run(
            "fofr/anything-v4.0:latest",  # Replace with your actual 3D render model
            input={
                "image": open(file_path, "rb"),
                "prompt": f"A 3D render of a kitchen with {cabinet} cabinets and a {worktop} worktop"
            }
        )

        # Extract image URL from response
        if isinstance(model_output, list):
            image_url = model_output[0]
        else:
            image_url = model_output

        return JSONResponse({"image_url": image_url})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
