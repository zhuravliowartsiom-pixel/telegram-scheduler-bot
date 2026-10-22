import asyncio
import logging
from datetime import datetime

from aiogram import Bot

from telegram_scheduler_bot.config import Settings, load_settings
from telegram_scheduler_bot.delivery_state import DeliveryState
from telegram_scheduler_bot.message_format import format_schedule
from telegram_scheduler_bot.sheets import get_today_schedule


logger = logging.getLogger(__name__)


async def send_today(
    bot: Bot,
    settings: Settings,
    state: DeliveryState,
) -> None:
    today = datetime.now(settings.timezone).date()

    pending = [
        chat_id
        for chat_id in settings.target_chat_ids
        if not state.was_sent(today, chat_id)
    ]

    if not pending:
        logger.info("Расписание на %s уже отправлено всем получателям", today)
        return

    schedule = await asyncio.to_thread(get_today_schedule)

    if schedule["date"] != today.isoformat():
        raise ValueError("Дата расписания не совпадает с датой рассылки")

    text = format_schedule(schedule)
    failed = 0

    for chat_id in pending:
        if datetime.now(settings.timezone).date() != today:
            raise RuntimeError("Дата изменилась во время рассылки")

        try:
            await bot.send_message(chat_id=chat_id, text=text)
        except Exception as error:
            failed += 1
            logger.error(
                "Ошибка отправки: chat_id=%s, тип=%s",
                chat_id,
                type(error).__name__,
            )
            continue

        state.mark_sent(today, chat_id)
        logger.info("Сообщение отправлено: chat_id=%s", chat_id)

    if failed:
        raise RuntimeError(
            f"Не удалось отправить сообщение в {failed} чат(ов)"
        )


async def main() -> None:
    settings = load_settings()
    state = DeliveryState()

    async with Bot(token=settings.bot_token) as bot:
        await send_today(bot, settings, state)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    asyncio.run(main())
