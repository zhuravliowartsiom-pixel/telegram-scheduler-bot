import logging
from datetime import datetime

from aiogram import Bot

from telegram_scheduler_bot.config import Settings
from telegram_scheduler_bot.delivery_state import DeliveryState


logger = logging.getLogger(__name__)

REMINDER_TIMES = {"17:00", "17:30", "17:55"}
REMINDER_TEXT = "СЕГОДНЯ ЗАПИСЬ НА ВАХТЫ (＿ ＿*) Z z z"


async def send_due_reminders(
    bot: Bot,
    settings: Settings,
    state: DeliveryState,
    now: datetime | None = None,
) -> None:
    if now is None:
        now = datetime.now(settings.timezone)
    else:
        if now.tzinfo is None:
            raise ValueError("Для проверки нужна дата с часовым поясом")
        now = now.astimezone(settings.timezone)

    if now.weekday() != 6:
        return

    slot = now.strftime("%H:%M")
    if slot not in REMINDER_TIMES:
        return

    day = now.date()

    for chat_id in settings.target_chat_ids:
        if state.reminder_was_sent(
            day, slot, chat_id, settings.target_thread_id
        ):
            continue

        try:
            await bot.send_message(
                chat_id=chat_id,
                message_thread_id=settings.target_thread_id,
                text=REMINDER_TEXT,
            )
        except Exception as error:
            logger.error(
                "Ошибка напоминания: время=%s, тип=%s",
                slot,
                type(error).__name__,
            )
            continue

        state.mark_reminder_sent(
            day, slot, chat_id, settings.target_thread_id
        )
        logger.info("Воскресное напоминание отправлено: время=%s", slot)
