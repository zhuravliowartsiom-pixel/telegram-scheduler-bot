import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path


def normalize(value: str) -> str:
    return unicodedata.normalize("NFKC", value).strip().casefold().replace(
        "ё", "е"
    )


@lru_cache(maxsize=1)
def load_people() -> dict[str, str]:
    path = Path("secrets/people.json")
    data = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(data, dict) or not data:
        raise ValueError("Справочник должен быть непустым JSON-объектом")

    result = {}
    for surname, username in data.items():
        if not isinstance(surname, str) or not isinstance(username, str):
            raise ValueError("Фамилии и юзернеймы должны быть строками")

        name = normalize(surname)
        if not name or name in result:
            raise ValueError("Пустая или повторяющаяся фамилия в справочнике")

        if not re.fullmatch(r"@[A-Za-z0-9_]{5,32}", username):
            raise ValueError("Некорректный юзернейм в справочнике")

        result[name] = username

    return result


def one_typo(left: str, right: str) -> bool:
    if left == right:
        return True

    if abs(len(left) - len(right)) > 1:
        return False

    if len(left) == len(right):
        positions = [
            index
            for index, (a, b) in enumerate(zip(left, right))
            if a != b
        ]

        if len(positions) == 1:
            return True

        if len(positions) == 2:
            first, second = positions
            return (
                second == first + 1
                and left[first] == right[second]
                and left[second] == right[first]
            )

        return False

    shorter, longer = sorted((left, right), key=len)
    return any(
        longer[:index] + longer[index + 1:] == shorter
        for index in range(len(longer))
    )


def resolve_person(value: str) -> str:
    surname = normalize(value)
    people = load_people()

    if not surname:
        raise ValueError("Пустая фамилия")

    if surname in people:
        return people[surname]

    candidates = [
        name for name in people
        if one_typo(surname, name)
    ]

    if len(candidates) != 1:
        raise ValueError("Не удалось однозначно определить фамилию")

    return people[candidates[0]]


def resolve_people(value: str) -> list[str]:
    surnames = [
        part
        for part in re.split(r"[\s,;/]+", normalize(value))
        if part
    ]

    if not surnames:
        raise ValueError("Пустой список фамилий")

    return list(dict.fromkeys(
        resolve_person(surname) for surname in surnames
    ))
