"""
Flask-приложение портфолио (двуязычное: RU/EN).

Роуты:
  GET  /                              — редирект на язык по умолчанию (/ru/)
  GET  /<lang>/                       — главная (данные + проекты по категориям)
  GET  /<lang>/projects/<slug>/       — страница проекта (единый шаблон, itch-стиль)
  GET  /projects/<slug>/assets/<f>    — ассеты проекта (общие для всех языков)

Язык берётся из префикса URL, кладётся в g.lang и автоматически
подставляется в url_for() (см. url_value_preprocessor / url_defaults).

Запуск в деве:
    python app.py
Запуск на проде — через WSGI-сервер (см. README): gunicorn "app:app"
"""
from __future__ import annotations

from flask import (
    Flask,
    abort,
    g,
    redirect,
    render_template,
    send_from_directory,
    url_for,
)

from config import Config
from portfolio.content import (
    CATEGORY_KEYS,
    DEFAULT_LANG,
    LANGUAGES,
    ContentStore,
)


def portfolio_app(config: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)

    store = ContentStore(
        projects_dir=config.PROJECTS_DIR,
        content_dir=config.CONTENT_DIR,
        translations_dir=config.TRANSLATIONS_DIR,
        reload=config.RELOAD_CONTENT,
    )
    app.extensions["content"] = store

    # --- Обработка языка в URL -------------------------------------------
    # Достаём <lang> из URL в g.lang, чтобы view-функции его не тащили.
    @app.url_value_preprocessor
    def pull_lang(_endpoint, values):
        g.lang = DEFAULT_LANG
        if values and "lang" in values:
            # Ключ вынимаем всегда — иначе Flask передаст его во view-функцию.
            lang = values.pop("lang")
            if lang not in LANGUAGES:
                # Неизвестный префикс (/favicon.ico/, /wp-admin/ и т.п.) — не главная.
                abort(404)
            g.lang = lang

    # Автоматически подставляем текущий язык во все url_for(), где он ожидается.
    @app.url_defaults
    def add_lang(endpoint, values):
        if "lang" in values or not endpoint:
            return
        if app.url_map.is_endpoint_expecting(endpoint, "lang"):
            values["lang"] = g.get("lang", DEFAULT_LANG)

    # Значения, доступные во всех шаблонах.
    @app.context_processor
    def inject_globals():
        lang = g.get("lang", DEFAULT_LANG)
        return {
            "lang": lang,
            "profile": store.profile(lang),
            "t": store.translations(lang),
            "category_keys": CATEGORY_KEYS,
            "languages": LANGUAGES,
            "default_lang": DEFAULT_LANG,
            "site_base_url": config.SITE_BASE_URL,
        }

    # --- Роуты ------------------------------------------------------------
    @app.route("/")
    def root():
        return redirect(url_for("index", lang=DEFAULT_LANG))

    @app.route("/<lang>/")
    def index():
        lang = g.lang
        return render_template(
            "index.html",
            grouped=store.by_category(lang),
            total=len(store.projects(lang)),
        )

    @app.route("/<lang>/projects/<slug>/")
    def project(slug: str):
        item = store.get(g.lang, slug)
        if item is None:
            abort(404)
        return render_template("project.html", project=item)

    @app.route("/projects/<slug>/assets/<path:filename>")
    def project_asset(slug: str, filename: str):
        # Ассеты общие для всех языков — без языкового префикса.
        project_dir = config.PROJECTS_DIR / slug / "assets"
        if not project_dir.exists():
            abort(404)
        return send_from_directory(project_dir, filename)

    @app.errorhandler(404)
    def not_found(_err):
        return render_template("404.html"), 404

    return app


app = portfolio_app()


if __name__ == "__main__":
    # Дев-сервер. Для прода использовать gunicorn/uwsgi (см. README).
    app.run(host="127.0.0.1", port=5000, debug=app.config["DEBUG"])