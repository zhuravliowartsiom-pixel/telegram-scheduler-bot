import os
from urllib.parse import quote

from dotenv import load_dotenv
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account


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
    cell_range = quote(settings["GOOGLE_SHEETS_RANGE"], safe="")
    url = (
        f"https://sheets.googleapis.com/v4/spreadsheets/"
        f"{spreadsheet_id}/values/{cell_range}"
    )

    with AuthorizedSession(credentials) as session:
        response = session.get(url, timeout=30)

        if response.status_code != 200:
            print(f"Ошибка Google Sheets API: HTTP {response.status_code}")
            error = response.json().get("error", {})
            print("Статус:", error.get("status", "неизвестен"))
            return

        rows = response.json().get("values", [])

    print("Чтение выполнено успешно.")
    print("Получено строк:", len(rows))
    print("Максимум столбцов:", max((len(row) for row in rows), default=0))


if __name__ == "__main__":
    main()
