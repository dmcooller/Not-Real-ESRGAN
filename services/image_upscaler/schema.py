from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ModelName(str, Enum):
    RealESRGAN_x4plus = "RealESRGAN_x4plus"
    RealESRGAN_x4plus_anime_6B = "RealESRGAN_x4plus_anime_6B"
    RealESRGAN_x2plus = "RealESRGAN_x2plus"
    realesr_animevideov3 = "realesr-animevideov3"
    realesr_general_x4v3 = "realesr-general-x4v3"

class ModelEntity(BaseModel):
    model: Any
    netscale: int
    file_url: list[str]


class UpscaleRequest(BaseModel):
    model_name: ModelName | None = Field(default=ModelName.RealESRGAN_x4plus, title="Model name")
    denoise_strength: float | None = Field(default=0.5, title="Denoise strength",
        description="Denoise strength. 0 for weak denoise (keep noise), 1 for strong denoise ability. Only used for the realesr-general-x4v3 model")
    outscale: float | None = Field(default=4, title="The final upsampling scale of the image", description="The final upsampling scale of the image")
    tile: int | None = Field(default=0, title="Tile size", description="Tile size, 0 for no tile during testing")
    tile_pad: int | None = Field(default=10, title="Tile padding", description="Tile padding")
    pre_pad: int | None = Field(default=0, title="Pre padding size at each border", description="Pre padding size at each border")
    face_enhance: bool | None = Field(default=False, title="Use GFPGAN to enhance face", description="Use GFPGAN to enhance face")
    fp32: bool | None = Field(default=False, title="Use fp32 precision during inference", description="Use fp32 precision during inference. Default: fp16 (half precision).")
    alpha_upsampler: str | None = Field(default="realesrgan", title="The upsampler for the alpha channels", description="The upsampler for the alpha channels. Options: realesrgan | bicubic")
    ext: str | None = Field(default="auto", title="Image extension", description="Image extension. Options: auto | jpg | png, auto means using the same extension as inputs")
    gpu_id: int | None = Field(default=None, title="GPU device to use", description="GPU device to use (default=None) can be 0,1,2 for multi-gpu")

    # Allow to use `model_name` as a protected name
    model_config = ConfigDict(protected_namespaces=())
