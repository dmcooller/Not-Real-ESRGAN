from fastapi import APIRouter

from .endpoints import (
    image_upscale,
)

api_router = APIRouter()
api_router.include_router(image_upscale.router, tags=["image-upscale"])