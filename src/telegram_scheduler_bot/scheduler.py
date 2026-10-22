import asyncio
import logging
from datetime import datetime

from aiogram import Bot

from telegram_scheduler_bot.config import Settings
from telegram_scheduler_bot.delivery_state import DeliveryState
from telegram_scheduler_bot.send_today import send_today


logger = logging.getLogger(__name__)


async def run_scheduler(
    bot: Bot,
    settings: Settings,
    state: DeliveryState,
) -> None:
    logger.info(
        "Рассылка настроена на %s, часовой пояс %s",
        settings.daily_send_time.strftime("%H:%M"),
        settings.timezone.key,
    )

    while True:
        now = datetime.now(settings.timezone)
        due = now.time() >= settings.daily_send_time
        pending = any(
            not state.was_sent(now.date(), chat_id)
            for chat_id in settings.target_chat_ids
        )

        if due and pending:
            try:
                await send_today(bot, settings, state)
            except Exception as error:
                logger.error(
                    "Ошибка автоматической рассылки: %s. "
                    "Повторная попытка через 5 минут.",
                    type(error).__name__,
                )
                await asyncio.sleep(300)
                continue

        await asyncio.sleep(30)
