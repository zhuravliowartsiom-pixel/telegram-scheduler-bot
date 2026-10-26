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
    target_thread_id: int | None
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

    raw_thread = os.getenv("TELEGRAM_TARGET_THREAD_ID", "").strip()
    thread_id = None

    if raw_thread:
        try:
            thread_id = int(raw_thread)
        except ValueError:
            raise ValueError(
                "TELEGRAM_TARGET_THREAD_ID должен быть целым числом"
            ) from None

        if thread_id <= 0:
            raise ValueError("ID топика должен быть положительным")

        if len(target_ids) != 1:
            raise ValueError(
                "Для отправки в топик укажи ровно одну группу"
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
            "DAILY_SEND_TIME должен быть в формате ЧЧ:ММ"
        ) from None

    timezone_name = os.getenv("BOT_TIMEZONE", "Europe/Minsk").strip()
    try:
        timezone = ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError):
        raise ValueError("Некорректный BOT_TIMEZONE") from None

    return Settings(
        bot_token=token,
        allowed_chat_ids=allowed_ids,
        target_chat_ids=target_ids,
        target_thread_id=thread_id,
        daily_send_time=send_time,
        timezone=timezone,
    )
