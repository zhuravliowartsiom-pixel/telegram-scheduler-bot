import re
from datetime import time

from telegram_scheduler_bot.people import resolve_people


TIME_RANGE = re.compile(
    r"^\s*(\d{1,2}):(\d{2})\s*[-–—]\s*(\d{1,2}):(\d{2})\s*$"
)


def format_start(value: str) -> str:
    match = TIME_RANGE.fullmatch(value)
    if match is None:
        raise ValueError(f"Не удалось распознать время: {value!r}")

    start_hour, start_minute, end_hour, end_minute = map(
        int, match.groups()
    )
    time(start_hour, start_minute)
    time(end_hour, end_minute)

    hour = start_hour % 12 or 12

    if start_minute:
        return f"{hour}:{start_minute:02d}"

    return str(hour)


def format_schedule(schedule: dict) -> str:
    if not schedule["shifts"] or not schedule["patrol"]:
        raise ValueError("В расписании не заполнена вахта или обход")

    lines = ["вахта:"]

    for shift in schedule["shifts"]:
        start = format_start(shift["time"])
        usernames = resolve_people(shift["person"])
        lines.append(f"с {start} {' '.join(usernames)}")

    patrol = []
    for entry in schedule["patrol"]:
        patrol.extend(resolve_people(entry))

    patrol = list(dict.fromkeys(patrol))

    lines.extend(["", "обход:", " ".join(patrol)])
    return "\n".join(lines)
