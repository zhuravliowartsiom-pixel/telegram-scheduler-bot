import os
from datetime import datetime
from urllib.parse import quote
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

from telegram_scheduler_bot.day_selection import select_day
from telegram_scheduler_bot.message_format import format_schedule
from telegram_scheduler_bot.week_selection import select_current_week


def main() -> None:
    load_dotenv()
    today = datetime.now(ZoneInfo("Europe/Minsk")).date()

    names = (
        "GOOGLE_APPLICATION_CREDENTIALS",
        "GOOGLE_SPREADSHEET_ID",
        "GOOGLE_SHEETS_RANGE",
    )
    settings = {name: os.getenv(name, "").strip() for name in names}

    for name, value in settings.items():
        if not value:
            raise ValueError(f"Заполни {name} в .env")

    credentials = service_account.Credentials.from_service_account_file(
        settings["GOOGLE_APPLICATION_CREDENTIALS"],
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )

    spreadsheet_id = quote(settings["GOOGLE_SPREADSHEET_ID"], safe="")
    base_url = (
        f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}"
    )

    with AuthorizedSession(credentials) as session:
        response = session.get(
            base_url,
            params={"fields": "sheets.properties.title"},
            timeout=30,
        )

        if response.status_code != 200:
            print(f"Ошибка списка вкладок: HTTP {response.status_code}")
            print("Статус:", response.json().get("error", {}).get("status"))
            raise SystemExit(1)

        titles = [
            sheet["properties"]["title"]
            for sheet in response.json().get("sheets", [])
        ]
        title = select_current_week(titles, today=today)

        escaped_title = title.replace("'", "''")
        full_range = (
            f"'{escaped_title}'!{settings['GOOGLE_SHEETS_RANGE']}"
        )

        response = session.get(
            f"{base_url}/values/{quote(full_range, safe='')}",
            timeout=30,
        )

        if response.status_code != 200:
            print(f"Ошибка чтения ячеек: HTTP {response.status_code}")
            print("Статус:", response.json().get("error", {}).get("status"))
            raise SystemExit(1)

        rows = response.json().get("values", [])

    schedule = select_day(rows, today=today)
    print(format_schedule(schedule))


if __name__ == "__main__":
    main()
