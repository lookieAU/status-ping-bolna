import asyncio
import logging
import re
import html
import aiohttp
import feedparser
from datetime import datetime, timezone
from repository.db_mock import db_mock


class RSSMonitorService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db = db_mock
        self.seen_ids: set[str] = set()
        self.etags: dict[str, str] = {}
        self.last_modified: dict[str, str] = {}

        self.feeds = self.db.get_collection("feeds")
        self.llm_providers = self.db.get_collection("llm_providers")

    async def fetch_feed(self, session: aiohttp.ClientSession, url: str) -> str | None:
        headers = {}

        if url in self.etags:
            headers["If-None-Match"] = self.etags[url]
        if url in self.last_modified:
            headers["If-Modified-Since"] = self.last_modified[url]

        try:
            async with session.get(
                url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 304:
                    self.logger.info(f"Feed unchanged (304): {url}")
                    return None

                if resp.status != 200:
                    self.logger.error(f"Failed to fetch feed {url}: {resp.status}")
                    return None

                if etag := resp.headers.get("ETag"):
                    self.etags[url] = etag
                if lm := resp.headers.get("Last-Modified"):
                    self.last_modified[url] = lm

                return await resp.text()

        except Exception as e:
            self.logger.error(f"Error fetching feed {url}: {e}")
            return None

    def _autodetect_llm_provider(self, text: str) -> str:
        for provider in self.llm_providers:
            if any(keyword in text.lower() for keyword in provider["keywords"]):
                return provider["name"].upper()
        return "UNKNOWN"

    def _clean_html(self, text: str) -> str:
        text = html.unescape(text)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def parse_and_process(self, feed_text: str, feed_url: str):
        feed = feedparser.parse(feed_text)

        for entry in feed.entries.reverse():
            entry_id = entry.get("id") or entry.get("link")

            if entry_id in self.seen_ids:
                continue

            self.seen_ids.add(entry_id)

            service = feed.feed.get("title", feed_url)
            status_message = self._clean_html(
                entry.get("summary") or entry.get("description", "")
            )
            published = entry.get("published", datetime.now(timezone.utc).isoformat())
            llm_provider = self._autodetect_llm_provider(f"{service} {status_message}")

            self.logger.info(
                f"[{published}] Product: {service} [{llm_provider}]\nStatus: {status_message}"
            )

            self.db.insert_one(
                "status_updates",
                {
                    "source": "rss",
                    "feed_url": feed_url,
                    "entry_id": entry_id,
                    "timestamp": published,
                    "message": status_message,
                    "llm_provider": llm_provider,
                },
            )

    async def check_all_feeds(self):
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_feed(session, url) for url in self.feeds]
            results = await asyncio.gather(*tasks)

            for url, result in zip(self.feeds, results):
                if result:
                    self.parse_and_process(result, url)

    async def start(self, interval_seconds: int = 60):
        self.logger.info(f"RSS Conditional Poll Interval - {interval_seconds} seconds")
        while True:
            await self.check_all_feeds()
            await asyncio.sleep(interval_seconds)
