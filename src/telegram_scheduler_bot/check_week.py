import os
from urllib.parse import quote

from dotenv import load_dotenv
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

from telegram_scheduler_bot.week_selection import select_current_week


def main() -> None:
    load_dotenv()

    key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    spreadsheet_id = os.getenv("GOOGLE_SPREADSHEET_ID", "").strip()

    if not key_path or not spreadsheet_id:
        raise ValueError(
            "Заполни GOOGLE_APPLICATION_CREDENTIALS и GOOGLE_SPREADSHEET_ID"
        )

    credentials = service_account.Credentials.from_service_account_file(
        key_path,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )

    url = (
        "https://sheets.googleapis.com/v4/spreadsheets/"
        + quote(spreadsheet_id, safe="")
    )

    with AuthorizedSession(credentials) as session:
        response = session.get(
            url,
            params={"fields": "sheets.properties.title"},
            timeout=30,
        )

        if response.status_code != 200:
            print(f"Ошибка Google Sheets API: HTTP {response.status_code}")
            print("Статус:", response.json().get("error", {}).get("status"))
            return

        titles = [
            sheet["properties"]["title"]
            for sheet in response.json().get("sheets", [])
        ]

    print("Выбрана вкладка:", select_current_week(titles))


if __name__ == "__main__":
    main()
