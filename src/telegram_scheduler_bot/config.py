import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    bot_token: str
    allowed_chat_ids: frozenset[int]


def load_settings() -> Settings:
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise ValueError("Заполни TELEGRAM_BOT_TOKEN в .env")

    raw_ids = os.getenv("TELEGRAM_ALLOWED_CHAT_IDS", "")
    try:
        allowed_ids = frozenset(
            int(value.strip())
            for value in raw_ids.split(",")
            if value.strip()
        )
    except ValueError:
        raise ValueError(
            "TELEGRAM_ALLOWED_CHAT_IDS должен содержать целые числа через запятую"
        ) from None

    return Settings(bot_token=token, allowed_chat_ids=allowed_ids)
