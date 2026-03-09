from __future__ import annotations

from aiogram import Bot, Router
from aiogram.types import Message

from app.services.storage import Storage
from app.utils.text import contains_bad_language

router = Router(name="moderation")


def setup_moderation_handlers(bot: Bot, storage: Storage, discussion_chat: str, warn_text: str):
    @router.message()
    async def moderate(message: Message) -> None:
        chat_match = False
        if isinstance(discussion_chat, str):
            if discussion_chat.startswith("@"):
                chat_match = (message.chat.username or "").lower() == discussion_chat.lstrip("@").lower()
            else:
                chat_match = str(message.chat.id) == discussion_chat
        else:
            chat_match = message.chat.id == discussion_chat

        if not chat_match:
            return
        if not message.text:
            return
        if not contains_bad_language(message.text):
            return
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        finally:
            await storage.add_moderation_event(
                user_id=message.from_user.id if message.from_user else None,
                username=message.from_user.username if message.from_user else None,
                text=message.text,
                action="delete_bad_language",
            )
        await bot.send_message(chat_id=message.chat.id, text=warn_text)

    return router
