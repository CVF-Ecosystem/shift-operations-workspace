from fastapi import APIRouter
from workspace_api.config import settings
router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok", "mode": settings.ai_mode, "service": "workspace-api"}
