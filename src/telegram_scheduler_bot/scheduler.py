import asyncio
import logging
from datetime import datetime

from aiogram import Bot

from telegram_scheduler_bot.config import Settings
from telegram_scheduler_bot.delivery_state import DeliveryState
from telegram_scheduler_bot.reminders import send_due_reminders
from telegram_scheduler_bot.send_today import send_today


logger = logging.getLogger(__name__)


async def run_daily(
    bot: Bot,
    settings: Settings,
    state: DeliveryState,
) -> None:
    while True:
        delay = 30

        try:
            now = datetime.now(settings.timezone)
            due = now.time() >= settings.daily_send_time
            pending = any(
                not state.was_sent(now.date(), chat_id)
                for chat_id in settings.target_chat_ids
            )

            if due and pending:
                await send_today(bot, settings, state)

        except Exception as error:
            logger.error(
                "Ошибка ежедневной рассылки: %s. "
                "Повторная попытка через 5 минут.",
                type(error).__name__,
            )
            delay = 300

        await asyncio.sleep(delay)


async def run_reminders(
    bot: Bot,
    settings: Settings,
    state: DeliveryState,
) -> None:
    while True:
        try:
            await send_due_reminders(bot, settings, state)
        except Exception as error:
            logger.error(
                "Ошибка проверки напоминаний: %s",
                type(error).__name__,
            )

        await asyncio.sleep(15)


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
    logger.info(
        "Воскресные напоминания: 17:00, 17:30, 17:55; пояс %s",
        settings.timezone.key,
    )

    async with asyncio.TaskGroup() as group:
        group.create_task(run_daily(bot, settings, state))
        group.create_task(run_reminders(bot, settings, state))
