import re
from datetime import date, datetime
from zoneinfo import ZoneInfo


DATE_PATTERN = re.compile(r"\b\d{2}\.\d{2}\.\d{4}\b")


def select_day(
    rows: list[list[str]],
    today: date | None = None,
) -> dict:
    if today is None:
        today = datetime.now(ZoneInfo("Europe/Minsk")).date()

    blocks = []
    current = None

    for row in rows:
        cells = [str(value).strip() for value in row]
        cells += [""] * max(0, 4 - len(cells))
        label, time, duty, patrol = cells[:4]

        if label:
            current = None
            match = DATE_PATTERN.search(label)
            if match:
                block_date = datetime.strptime(
                    match[0], "%d.%m.%Y"
                ).date()
                current = {
                    "date": block_date.isoformat(),
                    "label": label,
                    "shifts": [],
                    "patrol": [],
                }
                if block_date == today:
                    blocks.append(current)

        if current is None:
            continue

        if time or duty:
            if not time or not duty:
                raise ValueError(
                    f"Неполная смена в блоке: {current['label']}"
                )
            current["shifts"].append({
                "time": time,
                "person": duty,
            })

        if patrol:
            current["patrol"].append(" ".join(patrol.split()))

    if len(blocks) != 1:
        raise ValueError(
            f"Ожидался один блок на {today:%d.%m.%Y}, "
            f"найдено: {len(blocks)}"
        )

    result = blocks[0]
    if not result["shifts"] or not result["patrol"]:
        raise ValueError("В выбранном дне не заполнена вахта или обход")

    return result
