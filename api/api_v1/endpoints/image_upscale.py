from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from services.image_upscaler.schema import UpscaleRequest
from services.image_upscaler.upscaler import upscale

router = APIRouter()

@router.post("/upscale/")
async def upscale_image(
    file: UploadFile = File(...),
    params: UpscaleRequest = Depends(UpscaleRequest),
):
    content = await file.read()
    try:
        img, ext = upscale(content, params)
    except RuntimeError as error:
        raise HTTPException(status_code=500, detail=f"Error: {error}") from error

    return StreamingResponse(img, media_type=f"image/{ext}")
