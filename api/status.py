from fastapi import APIRouter
import logging
from services.status import StatusService

router = APIRouter(prefix="/status")
logger = logging.getLogger(__name__)


@router.get("/all")
@router.get("/all/")
async def get_all_statuses():
    status_service = StatusService()
    statuses = await status_service.get_all_statuses()
    return {"statuses": list(reversed(statuses))}
