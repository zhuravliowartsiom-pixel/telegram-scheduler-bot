import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from telegram_scheduler_bot.config import load_settings


logger = logging.getLogger(__name__)


async def main() -> None:
    settings = load_settings()
    dispatcher = Dispatcher()

    @dispatcher.message(CommandStart())
    async def handle_start(message: Message) -> None:
        if message.chat.id not in settings.allowed_chat_ids:
            logger.warning(
                "Доступ запрещён: chat_id=%s",
                message.chat.id,
            )
            return

        await message.answer("Бот работает. Доступ разрешён.")

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
