"""
Расчёт стажа для секции «Опыт работы», в стиле hh.ru.

Идея: в profile.<lang>.yaml у каждой записи опыта задаются машинные даты

    start: 2023-05      # год-месяц (месяц можно опустить: 2023 значит январь)
    end:                # пусто, «сейчас», present: работа по текущий день

а подпись периода («май 2023 – по настоящее время») и длительность
(«3 года 4 месяца») считаются здесь. Если у записи вместо start/end указан
готовый текст `period`, он остаётся как есть, длительность не считается.

Месяц учитывается целиком, как на hh: январь-февраль это 2 месяца.
Общий стаж считается по объединённым интервалам, поэтому параллельные
или пересекающиеся места работы не удваивают его.

Точка «сегодня» передаётся аргументом `today` (по умолчанию текущая дата),
поэтому длительности не нужно кэшировать: они пересчитываются на каждый запрос.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Iterable

# Слова, означающие «по настоящее время» в поле end.
_PRESENT_WORDS = {
    "", "now", "present", "current", "today",
    "сейчас", "настоящее время", "по настоящее время", "н.в.", "нв",
}

# Локализация подписей: месяцы, «по настоящее время», формы «год»/«месяц».
_LOCALES: dict[str, dict[str, Any]] = {
    "ru": {
        "months": [
            "январь", "февраль", "март", "апрель", "май", "июнь",
            "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь",
        ],
        "present": "по настоящее время",
        "dash": " – ",
        # Формы для 1 / 2-4 / 5-20 (русское склонение).
        "year_forms": ("год", "года", "лет"),
        "month_forms": ("месяц", "месяца", "месяцев"),
    },
    "en": {
        "months": [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December",
        ],
        "present": "present",
        "dash": " – ",
        "year_forms": ("year", "years", "years"),
        "month_forms": ("month", "months", "months"),
    },
}
_DEFAULT_LOCALE = "ru"


def _locale(lang: str) -> dict[str, Any]:
    return _LOCALES.get(lang, _LOCALES[_DEFAULT_LOCALE])


# --- разбор дат ---------------------------------------------------------


def parse_month(value: Any) -> tuple[int, int] | None:
    """
    Год и месяц из значения YAML. Понимает date/datetime (YAML сам разбирает
    полные даты вида 2023-05-01), число 2023 и строки «2023-05», «2023.05»,
    «05.2023», «05/2023», «2023». Возвращает None, если разобрать не удалось.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.year, value.month
    if isinstance(value, date):
        return value.year, value.month
    if isinstance(value, int):
        return (value, 1) if 1000 <= value <= 9999 else None

    text = str(value).strip()
    if not text:
        return None

    numbers = re.findall(r"\d+", text)
    if not numbers:
        return None

    if len(numbers[0]) == 4:                      # 2023-05, 2023
        year = int(numbers[0])
        month = int(numbers[1]) if len(numbers) > 1 else 1
    elif len(numbers[-1]) == 4:                   # 05.2023
        year = int(numbers[-1])
        month = int(numbers[0])
    else:
        return None

    if not 1 <= month <= 12:
        return None
    return year, month


def _as_list(value: Any) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _highlight_groups(value: Any) -> list[dict]:
    """
    Пункты опыта в единой форме [{title, items}]. Строки подряд собираются
    в группу без заголовка, словарь {group, items} даёт группу с заголовком.
    """
    groups: list[dict] = []

    def plain() -> dict:
        """Текущая группа без заголовка, куда складываются строки подряд."""
        if not groups or groups[-1]["title"]:
            groups.append({"title": "", "items": []})
        return groups[-1]

    for entry in _as_list(value):
        if isinstance(entry, dict):
            items = [str(i) for i in _as_list(entry.get("items")) if str(i).strip()]
            if items:
                title = entry.get("group") or entry.get("title") or ""
                groups.append({"title": str(title), "items": items})
        elif str(entry).strip():
            plain()["items"].append(str(entry))

    return groups


def _is_present(value: Any) -> bool:
    """True, если поле end означает «работаю до сих пор»."""
    if value is None:
        return True
    if isinstance(value, bool):
        return value
    return str(value).strip().lower().strip(".") in _PRESENT_WORDS


def _index(year_month: tuple[int, int]) -> int:
    """Порядковый номер месяца, чтобы считать интервалы обычной арифметикой."""
    year, month = year_month
    return year * 12 + (month - 1)


# --- форматирование -----------------------------------------------------


def _plural(value: int, forms: tuple[str, str, str]) -> str:
    """Форма слова для числа: (1, 2-4, 5-20). Работает и для английского."""
    if value % 10 == 1 and value % 100 != 11:
        form = forms[0]
    elif 2 <= value % 10 <= 4 and not 12 <= value % 100 <= 14:
        form = forms[1]
    else:
        form = forms[2]
    return f"{value} {form}"


def format_duration(months: int, lang: str) -> str:
    """«3 года 4 месяца», «3 years 4 months». Для 0 и меньше пустая строка."""
    if months <= 0:
        return ""
    loc = _locale(lang)
    years, rest = divmod(months, 12)

    parts: list[str] = []
    if years:
        parts.append(_plural(years, loc["year_forms"]))
    if rest or not years:
        parts.append(_plural(rest, loc["month_forms"]))
    return " ".join(parts)


def format_period(
    start: tuple[int, int],
    end: tuple[int, int] | None,
    lang: str,
) -> str:
    """«май 2023 – по настоящее время», «май 2023 – август 2024»."""
    loc = _locale(lang)

    def label(year_month: tuple[int, int]) -> str:
        year, month = year_month
        return f"{loc['months'][month - 1]} {year}"

    right = label(end) if end else loc["present"]
    return f"{label(start)}{loc['dash']}{right}"


# --- подсчёт стажа ------------------------------------------------------


@dataclass
class _Span:
    """Интервал работы в «номерах месяцев», обе границы включительно."""
    first: int
    last: int

    @property
    def months(self) -> int:
        return max(0, self.last - self.first + 1)


def _span(item: Any, today: date) -> _Span | None:
    """Интервал одной записи опыта. None, если дат нет или они некорректны."""
    if not isinstance(item, dict):
        return None
    start = parse_month(item.get("start"))
    if start is None:
        return None

    end_raw = item.get("end")
    end = None if _is_present(end_raw) else parse_month(end_raw)
    if end is None:
        end = (today.year, today.month)

    first, last = _index(start), _index(end)
    if last < first:                              # опечатка в датах, не считаем
        return None
    return _Span(first, last)


def _merged_months(spans: Iterable[_Span]) -> int:
    """Суммарная длина интервалов с объединением пересечений."""
    ordered = sorted(spans, key=lambda s: (s.first, s.last))
    total = 0
    current: _Span | None = None
    for span in ordered:
        if current is None:
            current = _Span(span.first, span.last)
        elif span.first <= current.last + 1:      # пересекаются или встык
            current.last = max(current.last, span.last)
        else:
            total += current.months
            current = _Span(span.first, span.last)
    if current is not None:
        total += current.months
    return total


def annotate(items: Any, lang: str, today: date | None = None) -> tuple[list, str]:
    """
    Копия списка опыта, где у каждой записи:
      period      подпись периода (если её не задали вручную в YAML),
      duration    «3 года 4 месяца» (пусто, если дат нет),
      highlights  список групп [{title, items}],
    плюс общий стаж строкой (пустая, если считать не из чего).
    """
    if not isinstance(items, list):
        return [], ""

    today = today or date.today()
    result: list = []
    spans: list[_Span] = []

    for item in items:
        if not isinstance(item, dict):
            result.append(item)
            continue

        enriched = dict(item)
        enriched["highlights"] = _highlight_groups(item.get("highlights"))
        span = _span(item, today)
        if span is not None:
            spans.append(span)
            enriched["duration"] = format_duration(span.months, lang)
            if not enriched.get("period"):
                start = parse_month(item.get("start"))
                end = None if _is_present(item.get("end")) else parse_month(item.get("end"))
                enriched["period"] = format_period(start, end, lang)
        else:
            enriched.setdefault("duration", "")
        result.append(enriched)

    return result, format_duration(_merged_months(spans), lang)


def with_experience(profile: dict, lang: str, today: date | None = None) -> dict:
    """
    Профиль с посчитанными периодами: `experience` дополнен длительностями,
    в `experience_total` общий стаж. Исходный словарь не меняется.
    """
    if not profile.get("experience"):
        return profile

    enriched = dict(profile)
    enriched["experience"], enriched["experience_total"] = annotate(
        profile["experience"], lang, today
    )
    return enriched