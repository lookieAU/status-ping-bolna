import logging
import math
from repository.db_mock import db_mock
from datetime import datetime
from datetime import timezone
from models.challenge import ChallengeRequest


class ChallengeService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db = db_mock
        self.llm_providers = self.db.get_collection("llm_providers")

    async def on_status_update_received(self, data: ChallengeRequest):
        try:
            if data.event.user is None:
                # Filter out status updates from unknown users
                return

            # Possible snippet for verifying the user from a users colleciton in DB
            # if self.db.find_one("users", {"uid": data.event.user}) is None:
            #     return

            try:
                normalized_utc_timestamp = datetime.fromtimestamp(
                    float(data.event.ts)
                ).isoformat()
            except Exception as e:
                self.logger.error(f"Error parsing timestamp: {e}")
                normalized_utc_timestamp = datetime.now(timezone.utc).isoformat()

            # Try to autodetect the LLM provider form the messaege
            llm_provider = self._autodetect_llm_provider(data.event.text)
            self.logger.info(
                f"Status Update [{llm_provider}] received from {data.event.user} at {normalized_utc_timestamp} UTC"
            )

            self.logger.info(f"Status Update Message: {data.event.text}")

            # Persist for analysis like failure rates, etc.
            self.db.insert_one(
                "status_updates",
                {
                    "source": "slack_integration",
                    "user": data.event.user,
                    "timestamp": normalized_utc_timestamp,
                    "message": data.event.text,
                    "llm_provider": llm_provider,
                },
            )
        except Exception as e:
            self.logger.error(f"Error processing status update: {e}")
            raise e

    def _autodetect_llm_provider(self, message: str) -> str:
        for provider in self.llm_providers:
            if any(keyword in message.lower() for keyword in provider["keywords"]):
                return provider["name"].upper()
        return "UNKNOWN"
