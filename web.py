import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.api_v1.api import api_router
from logger import get_uvicorn_log_config, init_logger
from settings import settings

init_logger()

app = FastAPI(
    title=settings.PROJECT_NAME,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)
app.include_router(api_router, prefix=settings.API_V1_STR)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        "web:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        log_config=get_uvicorn_log_config(),
        reload=settings.APP_RELOAD,
    )