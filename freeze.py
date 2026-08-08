"""
Сборка статической версии сайта.

Flask-приложение рендерится в набор готовых HTML-файлов, которые отдаёт любой
статический хостинг, в том числе GitHub Pages.

    python freeze.py                                  # собрать в ./build
    python freeze.py --output dist                    # другая папка
    python freeze.py --base-url https://user.github.io  # абсолютный URL для og-тегов

Состав сборки:
    index.html                          переадресация с корня на язык по умолчанию
    <lang>/index.html                   главная
    <lang>/projects/<slug>/index.html   страницы проектов
    projects/<slug>/assets/...          файлы проектов (общие для языков)
    static/...                          css и js
    404.html                            страница ошибки, GitHub Pages берёт её из корня
    .nojekyll                           отключает обработку Jekyll на стороне Pages

Ассеты копируются напрямую из content/projects/<slug>/assets: в шаблонах и в
теле проектов пути к ним записаны вручную (/projects/<slug>/assets/...), а не
через url_for, поэтому обходом ссылок их не найти.

Ограничение: все пути к ассетам абсолютные от корня, поэтому сайт должен лежать
в корне домена (репозиторий <login>.github.io или свой домен). Для публикации в
подкаталоге вида user.github.io/repo пути пришлось бы переписывать на сборке.

Стаж в секции «Опыт работы» считается от текущей даты, то есть в статике он
фиксируется на момент сборки. Чтобы он не устаревал, сборку стоит повторять по
расписанию (см. .github/workflows/pages.yml).
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

from app import portfolio_app
from config import BASE_DIR, Config
from portfolio.content import DEFAULT_LANG, LANGUAGES

DEFAULT_OUTPUT = BASE_DIR / "build"

# URL, который заведомо не совпадает ни с одним роутом: нужен, чтобы получить
# отрендеренную страницу 404.
_MISSING_URL = "/__not-found__/"

# Начало файла-указателя Git LFS. Если содержимое ассета выглядит так, значит
# при выкачивании репозитория не подтянулись реальные файлы.
_LFS_POINTER = b"version https://git-lfs.github.com/spec/v1"


def _build_app(base_url: str):
    """Приложение в режиме прода: контент читается с диска один раз."""

    class FreezeConfig(Config):
        DEBUG = False
        RELOAD_CONTENT = False
        SITE_BASE_URL = base_url.rstrip("/")

    return portfolio_app(FreezeConfig)


def _page_urls(store) -> list[str]:
    """Все страницы сайта: главная и проекты на каждом языке."""
    urls: list[str] = []
    for lang in LANGUAGES:
        urls.append(f"/{lang}/")
        for project in store.projects(lang):
            urls.append(f"/{lang}/projects/{project.slug}/")
    return urls


def _write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _prepare_output(output: Path, force: bool) -> None:
    """Очистка папки сборки. Чужую непустую папку не трогаем без --force:
    признак нашей сборки это файл .nojekyll в корне."""
    if not output.exists():
        output.mkdir(parents=True)
        return

    if not output.is_dir():
        sys.exit(f"Путь сборки занят файлом: {output}")

    entries = list(output.iterdir())
    if entries and not (output / ".nojekyll").exists() and not force:
        sys.exit(
            f"Папка {output} не пуста и не похожа на прошлую сборку.\n"
            f"Укажи другую через --output или повтори с --force."
        )

    shutil.rmtree(output)
    output.mkdir(parents=True)


def _render_pages(app, output: Path) -> int:
    """Обход страниц через тестовый клиент. Каждый URL со слэшем на конце
    ложится в отдельную папку с index.html."""
    client = app.test_client()
    urls = _page_urls(app.extensions["content"])

    for url in urls:
        response = client.get(url)
        if response.status_code != 200:
            sys.exit(f"{url}: ответ {response.status_code}, сборка остановлена")
        _write(output / url.strip("/") / "index.html", response.data)

    response = client.get(_MISSING_URL)
    if response.status_code != 404:
        sys.exit(f"{_MISSING_URL}: ожидался 404, получен {response.status_code}")
    _write(output / "404.html", response.data)

    return len(urls) + 1


def _render_root_redirect(app, output: Path) -> None:
    """Корень сайта. Роут / отдаёт редирект, статикой его не воспроизвести,
    поэтому кладём страницу с мгновенной переадресацией."""
    store = app.extensions["content"]
    profile = store.profile(DEFAULT_LANG)
    title = profile.get("site_title") or profile.get("name") or "Portfolio"
    target = f"/{DEFAULT_LANG}/"

    html = f"""<!doctype html>
<html lang="{DEFAULT_LANG}">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <meta http-equiv="refresh" content="0; url={target}">
  <link rel="canonical" href="{target}">
  <script>location.replace("{target}");</script>
</head>
<body>
  <p><a href="{target}">{target}</a></p>
</body>
</html>
"""
    _write(output / "index.html", html.encode("utf-8"))


def _is_lfs_pointer(path: Path) -> bool:
    if path.stat().st_size > 1024:
        return False
    with open(path, "rb") as fh:
        return fh.read(len(_LFS_POINTER)) == _LFS_POINTER


def _copy_tree(source: Path, destination: Path) -> list[Path]:
    """Копия дерева файлов. Возвращает список скопированных файлов."""
    copied: list[Path] = []
    for item in source.rglob("*"):
        if item.is_dir():
            continue
        target = destination / item.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)
        copied.append(target)
    return copied


def _copy_assets(app, output: Path) -> tuple[int, list[Path]]:
    """Ассеты проектов и содержимое static/. Заодно проверка на указатели LFS:
    без git lfs pull вместо картинок в сборку уедут текстовые заглушки."""
    files: list[Path] = []

    static_dir = BASE_DIR / "static"
    if static_dir.exists():
        files += _copy_tree(static_dir, output / "static")

    projects_dir = Path(app.config["PROJECTS_DIR"])
    if projects_dir.exists():
        for project_dir in sorted(projects_dir.iterdir()):
            assets = project_dir / "assets"
            if project_dir.is_dir() and assets.is_dir():
                files += _copy_tree(assets, output / "projects" / project_dir.name / "assets")

    pointers = [f for f in files if _is_lfs_pointer(f)]
    return len(files), pointers


def freeze(output: Path, base_url: str, force: bool) -> None:
    app = _build_app(base_url)

    _prepare_output(output, force)
    pages = _render_pages(app, output)
    _render_root_redirect(app, output)
    assets, pointers = _copy_assets(app, output)
    (output / ".nojekyll").touch()

    total_mb = sum(f.stat().st_size for f in output.rglob("*") if f.is_file()) / 1024 / 1024
    print(f"Готово: {output}")
    print(f"  страниц: {pages + 1}")
    print(f"  файлов ассетов: {assets}")
    print(f"  размер: {total_mb:.1f} МБ")

    if pointers:
        print(f"\nВНИМАНИЕ: {len(pointers)} файлов выглядят как указатели Git LFS,")
        print("реальное содержимое не выкачано. Выполни `git lfs pull`.")
        for path in pointers[:5]:
            print(f"  {path.relative_to(output)}")
        if len(pointers) > 5:
            print(f"  ... и ещё {len(pointers) - 5}")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Собрать статическую версию сайта.")
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT,
        help=f"папка сборки (по умолчанию {DEFAULT_OUTPUT.name})",
    )
    parser.add_argument(
        "--base-url", default=os.environ.get("SITE_BASE_URL", ""),
        help="абсолютный URL сайта для og-тегов и canonical, напр. https://user.github.io",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="очистить папку сборки, даже если её содержимое не похоже на прошлую сборку",
    )
    args = parser.parse_args()

    freeze(args.output.resolve(), args.base_url, args.force)


if __name__ == "__main__":
    main()
