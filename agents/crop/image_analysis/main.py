from fastapi import FastAPI
from agents.crop.image_analysis.schemas import ImageAnalysisRequest, ImageAnalysisResponse
from agents.crop.image_analysis.service import analyze_images

app = FastAPI(title="Image Analysis Agent")

@app.post("/analyze", response_model=ImageAnalysisResponse)
async def analyze(req: ImageAnalysisRequest):
    result = analyze_images(req.image_inputs, req.crop_type, req.location)
    return ImageAnalysisResponse(**result)
