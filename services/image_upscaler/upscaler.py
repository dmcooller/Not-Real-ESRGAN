import io
import cv2
import logging
import os
from basicsr.archs.rrdbnet_arch import RRDBNet
from basicsr.utils.download_util import load_file_from_url
import numpy as np

logger = logging.getLogger(__name__)

from realesrgan import RealESRGANer
from realesrgan.archs.srvgg_arch import SRVGGNetCompact
from services.image_upscaler.schema import ModelEntity, UpscaleRequest, ModelName


def upscale(file: bytes, params: UpscaleRequest) -> tuple[io.BytesIO, str]:
    """Upscale the image using selected model and parameters.

    Returns:
        tuple: The upscaled image as a BytesIO object and the file extension.
    """

    model_entity = _get_model(params.model_name)
    model_path = _get_model_path(params.model_name, model_entity.file_url)

    # use dni to control the denoise strength
    dni_weight = None
    if params.model_name == ModelName.realesr_general_x4v3 and params.denoise_strength is not None and params.denoise_strength != 1:
        wdn_model_path = model_path.replace('realesr-general-x4v3', 'realesr-general-wdn-x4v3')
        model_path = [model_path, wdn_model_path]
        dni_weight = [params.denoise_strength, 1 - params.denoise_strength]

    # restorer
    upsampler = RealESRGANer(
        scale=model_entity.netscale,
        model_path=model_path,
        dni_weight=dni_weight,
        model=model_entity.model,
        tile=params.tile,
        tile_pad=params.tile_pad,
        pre_pad=params.pre_pad,
        half=not params.fp32,
        gpu_id=params.gpu_id
    )

    nparr = np.fromstring(file, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

    if len(img.shape) == 3 and img.shape[2] == 4:
        img_mode = 'RGBA'
    else:
        img_mode = None

    try:
        if params.face_enhance:
            face_enhancer = _load_face_enhancer(params.outscale, upsampler)
            _, _, output = face_enhancer.enhance(img, has_aligned=False, only_center_face=False, paste_back=True)
        else:
            output, _ = upsampler.enhance(img, outscale=params.outscale)
    except RuntimeError as error:
        logger.error('Error: %s', error)
        raise error

    extension = _get_extension(img_mode, params.ext)

    # Convert the upscaled image back into a format that can be returned
    is_success, buffer = cv2.imencode(f'.{extension}', output)
    if not is_success:
        raise RuntimeError('Error encoding the image')

    return io.BytesIO(buffer), extension


def _get_model(model_name: ModelName) -> ModelEntity:
    """Get the model entity according to the model name."""

    if model_name == ModelName.RealESRGAN_x4plus:  # x4 RRDBNet model
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        netscale = 4
        file_url = ['https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.1/RealESRNet_x4plus.pth']
    elif model_name == ModelName.RealESRGAN_x2plus:  # x2 RRDBNet model
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=2)
        netscale = 2
        file_url = ['https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth']
    elif model_name == ModelName.RealESRGAN_x4plus_anime_6B:  # x4 RRDBNet model with 6 blocks
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=6, num_grow_ch=32, scale=4)
        netscale = 4
        file_url = ['https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth']
    elif model_name == ModelName.realesr_animevideov3:  # x4 VGG-style model (XS size)
        model = SRVGGNetCompact(num_in_ch=3, num_out_ch=3, num_feat=64, num_conv=16, upscale=4, act_type='prelu')
        netscale = 4
        file_url = ['https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth']
    elif model_name == ModelName.realesr_general_x4v3:  # x4 VGG-style model (S size)
        model = SRVGGNetCompact(num_in_ch=3, num_out_ch=3, num_feat=64, num_conv=32, upscale=4, act_type='prelu')
        netscale = 4
        file_url = [
            'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-wdn-x4v3.pth',
            'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth'
        ]
    else:
        raise ValueError("Invalid model name")
    return ModelEntity(model=model, netscale=netscale, file_url=file_url)

def _get_model_path(model_name: str, file_url: list[str]) -> str:
    """Determines the model path. If the model is not found, it will be downloaded from the file_url."""

    model_path = os.path.join('weights', model_name + '.pth')
    if not os.path.isfile(model_path):
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        for url in file_url:
            # model_path will be updated
            model_path = load_file_from_url(
                url=url, model_dir=os.path.join(root_dir, 'weights'), progress=True, file_name=None)
    return model_path

def _get_extension(img_mode: str, ext: str) -> str:
    """Determines the extension of the image."""

    if img_mode == 'RGBA':  # RGBA images should be saved in png format
        extension = 'png'
    elif ext == 'auto':
        extension = 'jpg'
    else:
        extension = ext
    return extension

def _load_face_enhancer(outscale: float | None, upsampler):
    """Load the face enhancer model."""

    from gfpgan import GFPGANer
    return GFPGANer(
            model_path='https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth',
            upscale=outscale,
            arch='clean',
            channel_multiplier=2,
            bg_upsampler=upsampler
        )
