import os
from urllib.parse import quote

from dotenv import load_dotenv
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

from telegram_scheduler_bot.week_selection import select_current_week


def main() -> None:
    load_dotenv()

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
            return

        titles = [
            sheet["properties"]["title"]
            for sheet in response.json().get("sheets", [])
        ]
        title = select_current_week(titles)

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
            return

        rows = response.json().get("values", [])

    print("Выбрана вкладка:", title)
    print("Чтение выполнено успешно.")
    print("Получено строк:", len(rows))
    print("Максимум столбцов:", max((len(row) for row in rows), default=0))


if __name__ == "__main__":
    main()
