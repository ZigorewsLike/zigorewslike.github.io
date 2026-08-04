"""
Конфигурация приложения.

Значения можно переопределить переменными окружения на сервере, например:
    FLASK_SECRET_KEY, SITE_BASE_URL и т.д.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    # Корни контента
    CONTENT_DIR = BASE_DIR / "content"
    PROJECTS_DIR = CONTENT_DIR / "projects"
    TRANSLATIONS_DIR = CONTENT_DIR / "translations"
    # Профиль и проекты хранятся в файлах на каждый язык:
    #   content/profile.<lang>.yaml
    #   content/projects/<slug>/index.<lang>.md

    # На проде поставь FLASK_DEBUG=0
    DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"

    # В деве контент перечитывается на каждый запрос (удобно править на лету).
    # На проде (DEBUG=0) контент кэшируется в памяти после первой загрузки.
    RELOAD_CONTENT = DEBUG

    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-me")

    # Абсолютный URL сайта — используется для og-тегов и canonical.
    SITE_BASE_URL = os.environ.get("SITE_BASE_URL", "")
