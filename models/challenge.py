from pydantic import BaseModel
from typing import Optional


class EventChallengeRequest(BaseModel):
    type: Optional[str] = None
    user: Optional[str] = None
    ts: Optional[str] = None
    text: Optional[str] = None


class ChallengeRequest(BaseModel):
    event: Optional[EventChallengeRequest] = None
