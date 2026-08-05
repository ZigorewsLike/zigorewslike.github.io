"""
Разметка в текстовых полях профиля: ссылки, абзацы, простой Markdown.

Описания в profile.<lang>.yaml проходят через Markdown, поэтому в них работают
[подписи](https://ссылки), **жирный**, списки. Голые адреса вида https://...
превращаются в ссылки сами. Новый абзац начинает пустая строка, так что длинный
текст можно спокойно переносить по строкам для читаемости.

Чтобы переносы дожили до рендера, многострочный текст в YAML пишется блоком:

    description: |
      Первый абзац.

      Второй абзац со [ссылкой](https://example.com).

В кавычках YAML склеивает строки в одну, и абзацы теряются.

Содержимое YAML пишет автор сайта, поэтому сырой HTML в тексте не вырезается.
"""
from __future__ import annotations

import re
from typing import Any

import markdown as md
from markupsafe import Markup

# sane_lists: список начинается только с новой строки, а не посреди абзаца.
_EXTENSIONS = ["sane_lists"]

# Голый адрес: не часть markdown-ссылки [текст](url), не <url>, не href="url".
# Обычные скобки в тексте, «(https://...)», разрешены.
_BARE_URL = re.compile(r"""(?<!\]\()(?<![<"'=])\bhttps?://[^\s<>"']+""")

# Знаки, которые обычно относятся к предложению, а не к адресу.
_TRAILING = ".,;:!?)"

_EXTERNAL_LINK = re.compile(r'<a href="(https?://[^"]+)">')

_SINGLE_PARAGRAPH = re.compile(r"\A<p>(.*)</p>\Z", re.S)

# Поля профиля, которые рендерятся как блок текста (могут содержать абзацы).
# tagline сюда не входит: он идёт в <meta name="description"> и должен
# оставаться простым текстом.
_BLOCK_FIELDS = ("description",)


def _autolink(text: str) -> str:
    """Голые адреса в <url>, чтобы Markdown сделал из них ссылки."""

    def wrap(match: re.Match) -> str:
        url = match.group(0)
        tail = ""
        while url and url[-1] in _TRAILING:
            # Закрывающая скобка адреса, как в вики-ссылках, остаётся внутри.
            if url[-1] == ")" and url.count(")") <= url.count("("):
                break
            tail = url[-1] + tail
            url = url[:-1]
        return f"<{url}>{tail}" if url else tail

    return _BARE_URL.sub(wrap, text)


def _external_blank(html: str) -> str:
    """Внешние ссылки открываются в новой вкладке, как и все ссылки на сайте."""
    return _EXTERNAL_LINK.sub(
        lambda m: f'<a href="{m.group(1)}" target="_blank" rel="noopener">', html
    )


def to_html(value: Any) -> Any:
    """Текст в HTML с абзацами. Не строки и пустые значения возвращаются как есть."""
    if not isinstance(value, str) or not value.strip():
        return value
    html = md.markdown(_autolink(value), extensions=_EXTENSIONS)
    return Markup(_external_blank(html))


def inline_html(value: Any) -> Any:
    """То же, но без <p> вокруг текста из одного абзаца: для строк внутри <li>."""
    html = to_html(value)
    if not isinstance(html, Markup):
        return html
    single = _SINGLE_PARAGRAPH.match(str(html))
    if single and "<p>" not in single.group(1):
        return Markup(single.group(1))
    return html


def _render_entry(entry: Any) -> Any:
    """Копия записи опыта, образования или публикации с размеченным текстом."""
    if not isinstance(entry, dict):
        return entry

    rendered = dict(entry)
    for key in _BLOCK_FIELDS:
        if key in rendered:
            rendered[key] = to_html(rendered[key])

    groups = rendered.get("highlights")
    if isinstance(groups, list):
        rendered["highlights"] = [
            {**g, "items": [inline_html(i) for i in g.get("items", [])]}
            if isinstance(g, dict) else inline_html(g)
            for g in groups
        ]
    return rendered


def render_profile(profile: dict) -> dict:
    """
    Копия профиля, где описания и пункты списков превращены в HTML.
    Исходный словарь не меняется.
    """
    rendered = dict(profile)

    for key in ("experience", "education", "publications"):
        section = rendered.get(key)
        if isinstance(section, list):
            rendered[key] = [_render_entry(entry) for entry in section]

    return rendered