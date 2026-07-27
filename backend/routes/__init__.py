"""
AUTOMA Routes Module
Aggregates all individual routers under a single API Router.
"""

from fastapi import APIRouter

from routes.projects import router as projects_router
from routes.videos import router as videos_router
from routes.settings import router as settings_router
from routes.logs import router as logs_router
from routes.hardware import router as hardware_router
from routes.files import router as files_router
from routes.video_templates import router as video_templates_router
from routes.jobs import router as jobs_router
from routes.history import router as history_router
from routes.export_profiles import router as export_profiles_router
from routes.subtitle_presets import router as subtitle_presets_router
from routes.assets import router as assets_router

api_router = APIRouter()

api_router.include_router(projects_router)
api_router.include_router(videos_router)
api_router.include_router(settings_router)
api_router.include_router(logs_router)
api_router.include_router(hardware_router)
api_router.include_router(files_router)
api_router.include_router(video_templates_router)
api_router.include_router(jobs_router)
api_router.include_router(history_router)
api_router.include_router(export_profiles_router)
api_router.include_router(subtitle_presets_router)
api_router.include_router(assets_router)
