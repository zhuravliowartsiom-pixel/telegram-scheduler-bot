import os
from dataclasses import dataclass
from datetime import time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    bot_token: str
    allowed_chat_ids: frozenset[int]
    target_chat_ids: tuple[int, ...]
    daily_send_time: time
    timezone: ZoneInfo


def parse_chat_ids(name: str) -> tuple[int, ...]:
    raw = os.getenv(name, "")

    try:
        values = [
            int(value.strip())
            for value in raw.split(",")
            if value.strip()
        ]
    except ValueError:
        raise ValueError(
            f"{name} должен содержать целые числа через запятую"
        ) from None

    if any(value == 0 for value in values):
        raise ValueError(f"{name} не должен содержать нулевой chat ID")

    return tuple(dict.fromkeys(values))


def load_settings() -> Settings:
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise ValueError("Заполни TELEGRAM_BOT_TOKEN в .env")

    allowed_ids = frozenset(parse_chat_ids("TELEGRAM_ALLOWED_CHAT_IDS"))
    target_ids = parse_chat_ids("TELEGRAM_TARGET_CHAT_IDS")

    if not target_ids:
        raise ValueError("Заполни TELEGRAM_TARGET_CHAT_IDS в .env")

    if not set(target_ids).issubset(allowed_ids):
        raise ValueError(
            "Все получатели рассылки должны быть "
            "в TELEGRAM_ALLOWED_CHAT_IDS"
        )

    raw_time = os.getenv("DAILY_SEND_TIME", "14:00").strip()
    try:
        if (
            len(raw_time) != 5
            or raw_time[2] != ":"
            or not raw_time[:2].isdigit()
            or not raw_time[3:].isdigit()
        ):
            raise ValueError

        send_time = time(
            hour=int(raw_time[:2]),
            minute=int(raw_time[3:]),
        )
    except ValueError:
        raise ValueError(
            "DAILY_SEND_TIME должен быть в формате ЧЧ:ММ, например 14:00"
        ) from None

    timezone_name = os.getenv("BOT_TIMEZONE", "Europe/Minsk").strip()
    try:
        timezone = ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError):
        raise ValueError(
            "BOT_TIMEZONE должен содержать действующий часовой пояс"
        ) from None

    return Settings(
        bot_token=token,
        allowed_chat_ids=allowed_ids,
        target_chat_ids=target_ids,
        daily_send_time=send_time,
        timezone=timezone,
    )
