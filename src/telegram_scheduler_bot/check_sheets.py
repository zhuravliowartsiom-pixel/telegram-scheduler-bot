from telegram_scheduler_bot.message_format import format_schedule
from telegram_scheduler_bot.sheets import get_today_schedule


def main() -> None:
    schedule = get_today_schedule()
    print(format_schedule(schedule))


if __name__ == "__main__":
    main()
