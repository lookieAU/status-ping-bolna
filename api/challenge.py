from fastapi import APIRouter, Request, Body
from models.challenge import ChallengeRequest
import logging
import asyncio

from services.challenge import ChallengeService

router = APIRouter(prefix="/status-event")
logger = logging.getLogger(__name__)


@router.post("")
@router.post("/")
async def challenge_endpoint(request: Request, data: ChallengeRequest = Body(...)):
    challenge_service = ChallengeService()
    asyncio.create_task(challenge_service.on_status_update_received(data))
    return {"status": "ok", "message": "Status Change request received"}
