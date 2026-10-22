def format_schedule(schedule: dict) -> str:
    lines = [
        f"Сегодня дежурят — {schedule['label']}",
        "",
        "Вахта:",
    ]

    for shift in schedule["shifts"]:
        time = shift["time"].replace("-", "–")
        lines.append(f"{time} — {shift['person']}")

    lines.extend(["", "Обход:"])
    lines.extend(schedule["patrol"])

    return "\n".join(lines)
