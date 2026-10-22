import asyncio
import logging

from aiogram import Bot

from telegram_scheduler_bot.config import Settings, load_settings
from telegram_scheduler_bot.message_format import format_schedule
from telegram_scheduler_bot.sheets import get_today_schedule


logger = logging.getLogger(__name__)


async def send_today(bot: Bot, settings: Settings) -> None:
    schedule = await asyncio.to_thread(get_today_schedule)
    text = format_schedule(schedule)

    failed = 0

    for chat_id in settings.target_chat_ids:
        try:
            await bot.send_message(chat_id=chat_id, text=text)
        except Exception as error:
            failed += 1
            logger.error(
                "Ошибка отправки: chat_id=%s, тип=%s",
                chat_id,
                type(error).__name__,
            )
        else:
            logger.info("Сообщение отправлено: chat_id=%s", chat_id)

    if failed:
        raise RuntimeError(
            f"Не удалось отправить сообщение в {failed} чат(ов)"
        )


async def main() -> None:
    settings = load_settings()

    async with Bot(token=settings.bot_token) as bot:
        await send_today(bot, settings)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    asyncio.run(main())
