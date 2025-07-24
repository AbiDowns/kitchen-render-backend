import replicate
import os
import tempfile
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Load your token from the environment variable
replicate.Client(api_token=os.environ.get("REPLICATE_API_TOKEN"))

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your Shopify domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_file(
    plan: UploadFile = File(...),
    cabinet: str = Form(...),
    worktop: str = Form(...)
):
    try:
        # Save temp file
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        temp.write(await plan.read())
        temp.close()

        # Replicate run
        output = replicate.run(
            "stability-ai/sdxl:latest",
            input={
                "image": open(temp.name, "rb"),
                "prompt": f"A modern kitchen with {cabinet} cabinets and {worktop} worktops",
                "guidance_scale": 7
            }
        )

        return JSONResponse(content={"image_url": output})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
