# Портфолио (Flask + Jinja2)

Двуязычный (RU/EN) сайт-портфолио с разделением проектов на категории
(**Python** и **Shaders / Graphics**). Главная страница + единый шаблон страницы
проекта в стиле itch.io (один шаблон — разное наполнение).

Языки живут в URL: `/ru/…` и `/en/…`, корень `/` редиректит на язык по умолчанию (`ru`).

## Структура

```
portfolio-site/
├── app.py                 # Flask-приложение (роуты, обработка языка)
├── config.py              # конфигурация (пути, DEBUG, кэш контента)
├── requirements.txt
├── portfolio/
│   ├── __init__.py
│   └── content.py         # загрузка проектов, профиля и UI-строк (по языкам)
├── content/
│   ├── profile.ru.yaml    # личные данные RU: опыт, образование, публикации, контакты
│   ├── profile.en.yaml    # то же на EN
│   ├── translations/
│   │   ├── ru.yaml        # строки интерфейса RU (nav, заголовки секций, метки)
│   │   └── en.yaml        # строки интерфейса EN
│   └── projects/
│       └── <slug>/
│           ├── index.ru.md  # frontmatter + тело (русская версия)
│           ├── index.en.md  # английская версия
│           └── assets/      # скриншоты/обложка/видео (общие для языков)
├── templates/
│   ├── base.html          # каркас (шапка, nav, переключатель языка, футер)
│   ├── index.html         # главная (данные + проекты + опыт/образование/публикации/контакты)
│   ├── project.html       # ЕДИНЫЙ шаблон страницы проекта
│   ├── _project_card.html # карточка проекта на главной
│   └── 404.html
└── static/
    ├── css/style.css      # нейтральная тема (правь под свой дизайн)
    └── js/filter.js       # фильтр проектов по категориям
```

## Языки (i18n)

- Поддерживаемые языки и язык по умолчанию задаются в `portfolio/content.py`
  (`LANGUAGES`, `DEFAULT_LANG`).
- **Строки интерфейса** — `content/translations/<lang>.yaml`.
- **Профиль** — `content/profile.<lang>.yaml`. Поля `site_title` (заголовок вкладки)
  и `brand` (подпись кнопки в шапке) задаются отдельно от `name`; если их не
  указать, оба берут `name`.
- **Проекты** — `index.<lang>.md` в папке проекта. Если файла для языка нет,
  берётся версия на языке по умолчанию (проект не пропадает из локали).
- Переключатель языка в шапке ведёт на ту же страницу в другой локали;
  добавлены теги `hreflang` для поисковиков.

Добавить язык (напр. `de`): допиши его в `LANGUAGES`, создай `translations/de.yaml`,
`profile.de.yaml` и `index.de.md` в проектах.

## Запуск (локально)

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows (PowerShell: .venv\Scripts\Activate.ps1)
pip install -r requirements.txt
python app.py
```

Открой http://127.0.0.1:5000

В dev-режиме контент перечитывается с диска на каждый запрос — правь `.md`/`.yaml`
и просто обновляй страницу.

## Как добавить проект

1. Создай папку `content/projects/мой-проект/` (имя папки = URL-slug).
2. Внутри — `index.ru.md` и/или `index.en.md` с frontmatter. Обязательны только
   `title` и `category` (`python` или `shaders`). Остальные поля опциональны.
3. Скриншоты/обложку/видео клади в `content/projects/мой-проект/assets/`
   и ссылайся по имени файла (`cover: cover.png`, `gallery: [shot1.png]`).
4. `cover` — обложка карточки на главной (кадрируется в 16:9), `banner` — широкая
   картинка в шапке страницы проекта (примерно 3:1, поверх неё идёт заголовок).
   Это разные файлы: без `banner` шапка рисуется без картинки.

Пример frontmatter — см. `content/projects/example-python-tool/index.ru.md`.
Все поддерживаемые поля описаны в шапке `portfolio/content.py`.

Тело `index.md` — обычный Markdown; можно вставлять сырой HTML
(`<iframe>`, `<video>`, `<canvas>`) для видео и интерактивных вставок.

## Категории

Задаются в `portfolio/content.py` → словарь `CATEGORIES`. Чтобы добавить/переименовать
категорию — правь его (ключ = значение поля `category`, значение = подпись в UI).

## Статическая сборка и GitHub Pages

Сайт не хранит состояния, поэтому его можно целиком отрендерить в HTML и
выложить на статический хостинг. Сборка:

```bash
python freeze.py                                     # в ./build
python freeze.py --base-url https://user.github.io   # с абсолютным URL для og-тегов
```

В `build/` попадают страницы всех языков (`<lang>/index.html`,
`<lang>/projects/<slug>/index.html`), ассеты проектов, `static/`, `404.html`,
`.nojekyll` и корневой `index.html` с переадресацией на язык по умолчанию
(роут `/` отдаёт редирект, статикой его не воспроизвести).
Подробности и ограничения описаны в шапке `freeze.py`.

Публикация настроена в `.github/workflows/pages.yml`: пуш в `master`/`main`
собирает сайт и деплоит его через GitHub Pages. В настройках репозитория нужно
выставить **Settings → Pages → Source: GitHub Actions**.

Что важно учитывать:

- **Сайт должен лежать в корне домена.** Пути к ассетам в шаблонах и в теле
  проектов абсолютные (`/projects/...`, `/static/...`), поэтому подходит
  репозиторий `<login>.github.io` или свой домен. В подкаталоге вида
  `user.github.io/repo` ссылки на картинки и css сломаются.
- **Git LFS.** Картинки и видео хранятся в LFS, в workflow стоит
  `checkout` с `lfs: true`. `freeze.py` дополнительно проверяет собранные файлы
  и падает, если вместо содержимого попались указатели LFS.
- **Стаж считается на дату сборки.** В workflow добавлен ежемесячный `cron`,
  который пересобирает сайт без изменений в репозитории.
- **Лимиты Pages:** до 1 ГБ на сайт и до 100 МБ на файл.

## Деплой на сервер (production)

Не используй встроенный дев-сервер на проде. Пример с gunicorn + nginx:

```bash
pip install gunicorn
FLASK_DEBUG=0 gunicorn -w 3 -b 127.0.0.1:8000 "app:app"
```

Переменные окружения:

| Переменная         | Назначение                                             |
|--------------------|--------------------------------------------------------|
| `FLASK_DEBUG`      | `0` на проде (включает кэш контента в памяти)           |
| `FLASK_SECRET_KEY` | секретный ключ Flask                                    |
| `SITE_BASE_URL`    | абсолютный URL сайта (для og:image при шаринге), напр. `https://example.com` |

Пример nginx (проксирование + отдача статики напрямую):

```nginx
server {
    listen 80;
    server_name example.com;

    location /static/ {
        alias /path/to/portfolio-site/static/;
        expires 7d;
    }
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $remote_addr;
    }
}
```

На Windows-сервере вместо gunicorn используй `waitress`:

```bash
pip install waitress
waitress-serve --listen=127.0.0.1:8000 app:app
```
