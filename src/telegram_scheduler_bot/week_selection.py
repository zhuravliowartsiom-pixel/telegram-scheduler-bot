import re
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


WEEK_TITLE = re.compile(
    r"^\s*(\d{2}\.\d{2}\.\d{4})\s*-\s*(\d{2}\.\d{2}\.\d{4})\s*$"
)


def select_current_week(
    titles: list[str],
    today: date | None = None,
) -> str:
    if today is None:
        today = datetime.now(ZoneInfo("Europe/Minsk")).date()

    matches = []

    for title in titles:
        match = WEEK_TITLE.fullmatch(title)
        if match is None:
            continue

        try:
            start = datetime.strptime(match[1], "%d.%m.%Y").date()
            end = datetime.strptime(match[2], "%d.%m.%Y").date()
        except ValueError:
            continue

        if start.weekday() != 0 or end != start + timedelta(days=6):
            continue

        if start <= today <= end:
            matches.append(title)

    if not matches:
        raise ValueError(
            f"Не найдена вкладка текущей недели для {today:%d.%m.%Y}"
        )

    if len(matches) > 1:
        raise ValueError("Найдено несколько вкладок текущей недели")

    return matches[0]
