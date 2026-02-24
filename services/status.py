import logging
from repository.db_mock import db_mock


class StatusService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db = db_mock

    async def get_all_statuses(self):
        return self.db.find_all("status_updates")
