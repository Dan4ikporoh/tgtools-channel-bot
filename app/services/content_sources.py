from __future__ import annotations

import html
import random
from datetime import datetime
from typing import Any

import feedparser
import httpx
import yaml
from bs4 import BeautifulSoup

from app.utils.text import normalize_text, safe_caption


class ContentProvider:
    def __init__(self, sources_path: str, default_language: str = "ru") -> None:
        self.sources_path = sources_path
        self.default_language = default_language
        with open(sources_path, "r", encoding="utf-8") as f:
            self.sources = yaml.safe_load(f)

    def categories(self) -> list[str]:
        return list(self.sources["categories"].keys())

    async def fetch_item(self, category: str, seen_ids: set[str]) -> dict[str, Any] | None:
        entry = self.sources["categories"][category]
        source_type = entry["type"]
        if source_type == "rss":
            return await self._from_rss(category, entry, seen_ids)
        if source_type == "holiday":
            return await self._holiday_item(category)
        if source_type == "nasa_apod":
            return await self._nasa_apod(category, seen_ids)
        if source_type == "wikimedia_featured":
            return await self._wikimedia_featured(category, seen_ids)
        return None

    async def _from_rss(self, category: str, entry: dict[str, Any], seen_ids: set[str]) -> dict[str, Any] | None:
        urls = list(entry.get("feed_urls", []))
        random.shuffle(urls)
        for feed_url in urls:
            parsed = feedparser.parse(feed_url)
            candidates = parsed.entries[:25]
            random.shuffle(candidates)
            for item in candidates:
                external_id = item.get("id") or item.get("guid") or item.get("link")
                if not external_id or external_id in seen_ids:
                    continue
                title = normalize_text(item.get("title", "Интересная находка"))
                summary = safe_caption(self._extract_summary(item), limit=700)
                media_url = self._extract_media(item)
                link = item.get("link")
                return {
                    "category": category,
                    "source_type": "rss",
                    "source_url": feed_url,
                    "external_id": external_id,
                    "title": title,
                    "text": self._render_caption(category, title, summary, link),
                    "media_url": media_url,
                    "link": link,
                }
        return None

    def _extract_summary(self, item: Any) -> str:
        raw = item.get("summary", item.get("description", ""))
        soup = BeautifulSoup(raw or "", "html.parser")
        text = soup.get_text(" ", strip=True)
        text = html.unescape(text)
        return normalize_text(text)

    def _extract_media(self, item: Any) -> str | None:
        media_candidates = item.get("media_content") or item.get("media_thumbnail") or []
        if media_candidates:
            first = media_candidates[0]
            if isinstance(first, dict):
                return first.get("url")
        soup = BeautifulSoup(item.get("summary", "") or item.get("description", "") or "", "html.parser")
        img = soup.find("img")
        if img and img.get("src"):
            return img["src"]
        return None

    async def _holiday_item(self, category: str) -> dict[str, Any] | None:
        today = datetime.utcnow().date()
        title = f"Сегодняшний повод для поста — {today.strftime('%d.%m')}"
        text = (
            "📅 День для быстрого вовлекающего поста.\n\n"
            "Спросите подписчиков, что они открыли для себя сегодня: новый бот, mini app, игру, мем или полезный сервис. "
            "Такие короткие посты часто хорошо собирают комментарии и реакции."
        )
        return {
            "category": category,
            "source_type": "holiday",
            "source_url": "internal",
            "external_id": f"holiday:{today.isoformat()}",
            "title": title,
            "text": text,
            "media_url": None,
        }

    async def _nasa_apod(self, category: str, seen_ids: set[str]) -> dict[str, Any] | None:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            response = await client.get("https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY")
            response.raise_for_status()
            data = response.json()
        external_id = f"nasa:{data.get('date')}"
        if external_id in seen_ids:
            return None
        media_url = data.get("hdurl") or data.get("url")
        return {
            "category": category,
            "source_type": "nasa_apod",
            "source_url": "https://api.nasa.gov/",
            "external_id": external_id,
            "title": data.get("title", "Космос дня"),
            "text": self._render_caption(category, data.get("title", "Космос дня"), data.get("explanation", ""), data.get("url")),
            "media_url": media_url if data.get("media_type") == "image" else None,
            "link": data.get("url"),
        }

    async def _wikimedia_featured(self, category: str, seen_ids: set[str]) -> dict[str, Any] | None:
        external_id = f"wikimedia:{datetime.utcnow().date().isoformat()}"
        if external_id in seen_ids:
            return None
        return {
            "category": category,
            "source_type": "wikimedia_featured",
            "source_url": "https://commons.wikimedia.org/",
            "external_id": external_id,
            "title": "Фото дня",
            "text": "🖼 Визуальный пост дня. Сохраняйте, делитесь и напишите в комментариях, что думаете.",
            "media_url": "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png",
        }

    def _render_caption(self, category: str, title: str, summary: str, link: str | None) -> str:
        label = self.sources["categories"][category]["label"]
        category_note = self.sources["categories"][category].get("note", "")
        body = f"🔥 {title}\n\n{summary}"
        if category_note:
            body += f"\n\n{category_note}"
        if link:
            body += f"\n\nИсточник: {link}"
        body += f"\n\n#{category} #{label.replace(' ', '')[:20]}"
        return safe_caption(body, limit=1024)
