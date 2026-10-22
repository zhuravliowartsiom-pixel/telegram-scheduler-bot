import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from telegram_scheduler_bot.config import load_settings
from telegram_scheduler_bot.message_format import format_schedule
from telegram_scheduler_bot.sheets import get_today_schedule


logger = logging.getLogger(__name__)


async def main() -> None:
    settings = load_settings()
    dispatcher = Dispatcher()

    def is_allowed(message: Message) -> bool:
        if message.chat.id in settings.allowed_chat_ids:
            return True

        logger.warning(
            "Доступ запрещён: chat_id=%s",
            message.chat.id,
        )
        return False

    @dispatcher.message(CommandStart())
    async def handle_start(message: Message) -> None:
        if not is_allowed(message):
            return

        await message.answer(
            "Бот работает. Доступ разрешён.\n"
            "/today — расписание на сегодня"
        )

    @dispatcher.message(Command("today"))
    async def handle_today(message: Message) -> None:
        if not is_allowed(message):
            return

        await message.answer("Получаю расписание на сегодня…")

        try:
            schedule = await asyncio.to_thread(get_today_schedule)
            text = format_schedule(schedule)
        except Exception as error:
            logger.error(
                "Не удалось получить расписание. Тип ошибки: %s",
                type(error).__name__,
            )
            await message.answer(
                "Не удалось получить расписание на сегодня. "
                "Проверьте таблицу и подключение к Google Sheets."
            )
            return

        await message.answer(text)

    logger.info(
        "Запуск бота. Разрешённых чатов: %s",
        len(settings.allowed_chat_ids),
    )

    async with Bot(token=settings.bot_token) as bot:
        await dispatcher.start_polling(
            bot,
            handle_as_tasks=False,
            allowed_updates=["message"],
        )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    asyncio.run(main())
