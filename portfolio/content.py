"""
Загрузка и разбор контента: проекты (Markdown + frontmatter), профиль и
UI-строки (YAML). Всё — с поддержкой нескольких языков.

Языки задаются в LANGUAGES; язык по умолчанию — DEFAULT_LANG.

Модель одного проекта:
  content/projects/<slug>/
      index.ru.md   — русская версия (frontmatter + тело на Markdown)
      index.en.md   — английская версия
      assets/       — картинки/скриншоты/видео (общие для всех языков)

Если файла для нужного языка нет — берётся версия на языке по умолчанию
(проект не «пропадает» из другой локали).

Frontmatter проекта (все поля кроме title/category опциональны):
  title:    "Название проекта"          (обязательно)
  category: python | shaders            (обязательно)
  summary:  "Короткое описание для карточки на главной"
  date:     2025-06                      (сортировка списка и подпись на карточке;
                                          строка или дата)
  tags:     [numpy, cli]
  tech:     [Python, PyTorch]            (стек — показывается отдельным блоком)
  cover:    cover.png                     (файл в assets/ — обложка карточки на главной)
  banner:   banner.png                    (файл в assets/ — широкая картинка шапки
                                           страницы проекта; без неё шапка без картинки)
  featured: true                         (поднять в начало списка)
  theme:    stars                        (оформление страницы: на <body> вешается
                                          класс theme-stars, правила в style.css)
  links:                                 (кнопки-ссылки сбоку, itch-стиль)
    - {label: "GitHub", url: "https://...", icon: github}
  gallery:                               (скриншоты; если нет — блок не рендерится)
    - {src: shot1.png, caption: "Главный экран"}
    - screenshot2.png
  video:    "https://www.youtube.com/embed/..."   (iframe-плеер; опционально)

Тело (Markdown) рендерится в HTML и может содержать сырой HTML
(iframe, <video>, <canvas>) — это доверенный контент автора.

Профиль:      content/profile.<lang>.yaml
UI-строки:    content/translations/<lang>.yaml
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

import frontmatter
import markdown as md
import yaml

from portfolio.experience import with_experience
from portfolio.richtext import render_profile

# Поддерживаемые языки: код -> подпись в переключателе. Первый = по умолчанию.
LANGUAGES: dict[str, str] = {
    "ru": "Русский",
    "en": "English",
}
DEFAULT_LANG = "ru"

# Ключи категорий (человекочитаемые подписи берутся из translations/<lang>.yaml).
# Порядок = порядок секций на главной.
CATEGORY_KEYS: list[str] = ["python", "shaders", "other"]

_MD_EXTENSIONS = ["fenced_code", "codehilite", "tables", "toc", "attr_list", "smarty"]


@dataclass
class Link:
    label: str
    url: str
    icon: str = "external"


@dataclass
class GalleryItem:
    src: str
    caption: str = ""


@dataclass
class Project:
    slug: str
    lang: str            # язык, на котором фактически загружено содержимое
    title: str
    category: str
    summary: str = ""
    date: str = ""
    date_label: str = ""   # дата в виде "июль 2026" для показа на карточке
    tags: list[str] = field(default_factory=list)
    tech: list[str] = field(default_factory=list)
    cover: str | None = None
    banner: str | None = None
    theme: str = ""      # имя оформления страницы, см. класс theme-* в style.css
    featured: bool = False
    links: list[Link] = field(default_factory=list)
    gallery: list[GalleryItem] = field(default_factory=list)
    video: str | None = None
    body_html: str = ""

    def asset_url(self, filename: str) -> str:
        """URL ассета внутри папки проекта (общий для всех языков)."""
        return f"/projects/{self.slug}/assets/{filename}"

    @property
    def cover_url(self) -> str | None:
        return self.asset_url(self.cover) if self.cover else None

    @property
    def banner_url(self) -> str | None:
        """Картинка шапки страницы проекта. Обложка карточки сюда не подставляется:
        у баннера другие пропорции, поэтому его задают отдельным файлом."""
        return self.asset_url(self.banner) if self.banner else None

    @property
    def _sort_key(self) -> tuple[int, int, int, str]:
        """Сначала свежие проекты; при равной дате выше featured, затем по слагу.
        Проекты без даты уходят в конец списка."""
        year, month = _date_parts(self.date)
        return (-year, -month, 0 if self.featured else 1, self.slug)


def _normalize_link(raw: Any) -> Link | None:
    if isinstance(raw, dict) and raw.get("url"):
        return Link(
            label=str(raw.get("label", raw["url"])),
            url=str(raw["url"]),
            icon=str(raw.get("icon", "external")),
        )
    return None


def _normalize_gallery_item(raw: Any) -> GalleryItem | None:
    if isinstance(raw, str):
        return GalleryItem(src=raw)
    if isinstance(raw, dict) and raw.get("src"):
        return GalleryItem(src=str(raw["src"]), caption=str(raw.get("caption", "")))
    return None


def _as_list(value: Any) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _stringify_date(value: Any) -> str:
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y-%m")
    return "" if value is None else str(value)


def _date_parts(value: str) -> tuple[int, int]:
    """Год и месяц из строки вида "2026-07" или "2026". Без даты - нули."""
    match = re.match(r"\s*(\d{4})(?:[-/.](\d{1,2}))?", value or "")
    if not match:
        return (0, 0)
    return (int(match.group(1)), int(match.group(2) or 0))


def _date_label(value: str, months: list[str]) -> str:
    """Подпись даты для карточки: "июль 2026". Без месяца или без списка
    названий остаётся исходная строка."""
    year, month = _date_parts(value)
    if not year:
        return value
    if not month or not (1 <= month <= len(months)):
        return str(year)
    return f"{months[month - 1]} {year}"


def _theme_name(value: Any) -> str:
    """Имя темы для класса на <body>. Лишние символы отбрасываются, потому что
    значение идёт прямо в атрибут class."""
    return re.sub(r"[^a-z0-9_-]", "", str(value or "").lower())


def _resolve_lang(lang: str) -> str:
    return lang if lang in LANGUAGES else DEFAULT_LANG


def _project_file(project_dir: Path, lang: str) -> Path | None:
    """Файл проекта на языке `lang`, с откатом на язык по умолчанию."""
    candidate = project_dir / f"index.{lang}.md"
    if candidate.exists():
        return candidate
    fallback = project_dir / f"index.{DEFAULT_LANG}.md"
    if fallback.exists():
        return fallback
    return None


def _load_project(project_dir: Path, lang: str, months: list[str]) -> Project | None:
    index = _project_file(project_dir, lang)
    if index is None:
        return None

    post = frontmatter.load(index)
    meta = post.metadata
    slug = project_dir.name

    title = meta.get("title")
    category = meta.get("category")
    if not title or not category:
        raise ValueError(
            f"Проект '{slug}' ({index.name}): обязательны поля 'title' и 'category'."
        )
    if category not in CATEGORY_KEYS:
        raise ValueError(
            f"Проект '{slug}': неизвестная категория '{category}'. "
            f"Допустимые: {', '.join(CATEGORY_KEYS)}."
        )

    body_html = md.markdown(post.content, extensions=_MD_EXTENSIONS)
    project_date = _stringify_date(meta.get("date"))

    gallery = [g for g in (_normalize_gallery_item(x) for x in _as_list(meta.get("gallery"))) if g]
    links = [l for l in (_normalize_link(x) for x in _as_list(meta.get("links"))) if l]

    return Project(
        slug=slug,
        lang=lang,
        title=str(title),
        category=str(category),
        summary=str(meta.get("summary", "")),
        date=project_date,
        date_label=_date_label(project_date, months),
        tags=[str(t) for t in _as_list(meta.get("tags"))],
        tech=[str(t) for t in _as_list(meta.get("tech"))],
        cover=meta.get("cover"),
        banner=meta.get("banner"),
        theme=_theme_name(meta.get("theme")),
        featured=bool(meta.get("featured", False)),
        links=links,
        gallery=gallery,
        video=meta.get("video"),
        body_html=body_html,
    )


def _load_yaml(path: Path) -> dict:
    if path.exists():
        with open(path, encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    return {}


class ContentStore:
    """
    Хранилище контента с опциональным кэшем, разбитое по языкам.

    reload=True  — перечитывать с диска на каждый вызов (dev).
    reload=False — загрузить один раз и держать в памяти (prod).
    """

    def __init__(
        self,
        projects_dir: Path,
        content_dir: Path,
        translations_dir: Path,
        *,
        reload: bool = True,
    ):
        self.projects_dir = Path(projects_dir)
        self.content_dir = Path(content_dir)
        self.translations_dir = Path(translations_dir)
        self.reload = reload
        self._projects_cache: dict[str, list[Project]] = {}
        self._profile_cache: dict[str, dict] = {}
        self._translations_cache: dict[str, dict] = {}

    # --- профиль -------------------------------------------------------
    def profile(self, lang: str) -> dict:
        lang = _resolve_lang(lang)
        if lang not in self._profile_cache or self.reload:
            data = _load_yaml(self.content_dir / f"profile.{lang}.yaml")
            if not data and lang != DEFAULT_LANG:
                data = _load_yaml(self.content_dir / f"profile.{DEFAULT_LANG}.yaml")
            self._profile_cache[lang] = data
        # Стаж считается от текущей даты, поэтому на каждый вызов.
        return render_profile(with_experience(self._profile_cache[lang], lang))

    # --- UI-строки -----------------------------------------------------
    def translations(self, lang: str) -> dict:
        lang = _resolve_lang(lang)
        if lang not in self._translations_cache or self.reload:
            data = _load_yaml(self.translations_dir / f"{lang}.yaml")
            if not data and lang != DEFAULT_LANG:
                data = _load_yaml(self.translations_dir / f"{DEFAULT_LANG}.yaml")
            self._translations_cache[lang] = data
        return self._translations_cache[lang]

    # --- проекты -------------------------------------------------------
    def _all(self, lang: str) -> list[Project]:
        lang = _resolve_lang(lang)
        if lang in self._projects_cache and not self.reload:
            return self._projects_cache[lang]

        months = [str(m) for m in _as_list(self.translations(lang).get("months"))]

        projects: list[Project] = []
        if self.projects_dir.exists():
            for child in sorted(self.projects_dir.iterdir()):
                if child.is_dir() and not child.name.startswith((".", "_")):
                    project = _load_project(child, lang, months)
                    if project:
                        projects.append(project)

        projects.sort(key=lambda p: p._sort_key)
        self._projects_cache[lang] = projects
        return projects

    def projects(self, lang: str, category: str | None = None) -> list[Project]:
        items = self._all(lang)
        if category:
            return [p for p in items if p.category == category]
        return items

    def by_category(self, lang: str) -> dict[str, list[Project]]:
        """Проекты, сгруппированные по категориям (в порядке CATEGORY_KEYS)."""
        grouped: dict[str, list[Project]] = {key: [] for key in CATEGORY_KEYS}
        for project in self._all(lang):
            grouped.setdefault(project.category, []).append(project)
        return grouped

    def get(self, lang: str, slug: str) -> Project | None:
        for project in self._all(lang):
            if project.slug == slug:
                return project
        return None