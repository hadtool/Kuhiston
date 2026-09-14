# PROGRESS — журнал сессий

> Правила: этот файл ТОЛЬКО дополняется, никогда не переписывается и не сокращается. Каждая сессия начинается с чтения последних 2-3 записей (чтобы понять, что уже сделано и в каком состоянии оставлен проект). В начале сессии — добавь новую запись с планом. В конце сессии — допиши в ту же запись, что реально сделано, что не получилось и почему.

Формат записи:
```
## Сессия N — дата
**План:** что собираюсь делать
**Сделано:** что реально сделано (со ссылками на файлы/коммиты, если есть)
**Не сделано / отложено:** что не получилось и почему
**Заметки для следующей сессии:** что важно знать, начиная следующую сессию
```

---

## Сессия 2 — 2026-09-14
**План:**
- Задача Этапа 0: «Настроить PostgreSQL + PostGIS локально и в выбранном бесплатном хостинге».
- Решить блокирующий вопрос из ISSUES.md про выбор хостинга.
- Поднять реальный PostgreSQL в песочнице (портативные бинарники) и проверить, что Django мигрирует на него через `DATABASE_URL`.
- Приготовить локальный PostGIS через docker-compose и настроить Django на PostGIS-движок.
- Следующая задача Этапа 0: переменные окружения (.env, MapTiler ключ — без хардкода).

**Сделано:**
- Выбор хостинга зафиксирован в DECISIONS.md, вопрос в ISSUES.md закрыт (Neon Free для БД, Render Free для приложения).
- Установлен и проверен реальный PostgreSQL 17.11 в песочнице: Django 6.1 подключён через `DATABASE_URL`, все встроенные миграции применены, таблицы созданы.
- `docker-compose.yml` — локальный PostGIS (`postgis/postgis:16-3.4`).
- `settings.py`: поддержка `DATABASE_URL` (dj-database-url), движок postgis — флагом `USE_POSTGIS_BACKEND=1`, без GEOS/GDAL приложение стартует на обычном postgres-движке.
- `.env.example` обновлён под Postgres.
- **Переменные окружения (следующая задача Этапа 0):** подключено `python-dotenv`, `backend/.env` (gitignored) автоматически загружается; `MAPTILER_API_KEY`, `DJANGO_SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, БД — только из окружения. Проверено: grep'ом в backend нет захардкоженных ключей; `.env` реально читается (`DEBUG`/`KEY`/`DB engine` из окружения); `runserver` отвечает HTTP 200 на sqlite-fallback. В ISSUES.md добавлено предупреждение о ротации ключа из `tajikistan-map-3d.html` перед публикацией.

**Не сделано / отложено:**
- Живая проверка PostGIS-расширения в БД и PostGIS-движка Django невозможна в песочнице: нет GEOS/GDAL/PostGIS-бинарников (и нет apt/docker/gcc). Это требует машины основателя (docker compose) или Neon-БД. Ограничение записано в DECISIONS.md.
- Аккаунт Neon/Render и реальный `DATABASE_URL` от основателя — чтобы доподлинно проверить хостинг. Задача «PostgreSQL+PostGIS» остаётся `[ ]` в TASKS.md до финальной проверки PostGIS на машине/хостинге.

**Сделано дополнительно (i18n и бренд, тоже Этап 0):**
- **i18n:** добавлен `LocaleMiddleware`, context processor `django.template.context_processors.i18n`, маршрут `/i18n/setlang/`. Созданы `frontend/locale/{ru,en,tg}/LC_MESSAGES/django.po` + скомпилированы `.mo`; `frontend/templates/base.html` — базовый шаблон с переключателем языка. Проверено: `gettext` отдаёт правильные переводы для ru/en/tg. `makemessages` сканирует только текущий каталог — прогонять его из `frontend/templates` (`manage.py makemessages -l ru -l en -l tg --extension html`).
- **Бренд:** `backend/kuhiston/brand.py` — единственное место с названием (`APP_NAME="Kuhiston"`) и локализованными слоганами (`APP_TAGLINE`); context processor раздаёт их в шаблоны. `base.html` использует `{{ brand_name }}`/`{{ brand_tagline }}`, больше нигде название не хардкодится. Проверено рендером с языком tg.

**Заметки для следующей сессии:** Этап 0 почти полностью закрыт. Следующие задачи — Этап 1 «Модель данных и админка/волонтёрская панель». Перед моделью "Место" не забыть ограничение про PostGIS/GEOS-GDAL (см. DECISIONS.md): пространственные поля (PointField) заработают только с PostGIS-движком и GEOS/GDAL. Проверка Django↔Postgres в песочнице делалась портативными бинарниками postgres 17.11 (Zonky/maven, лежат в maven central `io/zonky/test/postgres/embedded-postgres-binaries-linux-amd64`), PostGIS в них нет.

---

## Сессия 1 — 2026-09-13
**План:**
- Зафиксировать выбор бэкенда (Django vs FastAPI), закрыть вопрос в ISSUES.md.
- Инициализировать git-репозиторий и базовую структуру проекта (бэкенд + фронтенд) — первая задача Этапа 0 из TASKS.md.
- Проверить, что бэкенд реально запускается (runserver), отметить задачу `[x]`.

**Сделано:**
- В DECISIONS.md зафиксирован бэкенд: Django + Django REST Framework (встроенная админка для волонтёрской панели, i18n, роли, ORM+миграции, django.contrib.gis для PostGIS).
- В ISSUES.md пункт про Django/FastAPI отмечен как решённый.
- Инициализирован git-репозиторий (`git init`, ветка main), первый коммит `ba24e91`.
- Структура проекта:
  - `backend/` — Django 6.1 + DRF 3.18, виртуальное окружение `.venv`, `requirements.txt`.
  - `backend/kuhiston/settings.py` — SECRET_KEY/DEBUG/ALLOWED_HOSTS через переменные окружения, DRF в INSTALLED_APPS, i18n (ru/en/tg, `LANGUAGE_CODE='ru'`, `TIME_ZONE='Asia/Dushanbe'`), TEMPLATES/STATICFILES_DIRS указывают на `frontend/`.
  - `backend/.env.example` — шаблон переменных окружения (Django, БД, MapTiler).
  - `frontend/` — папки `templates/`, `static/css|js|img/`, `locale/`.
  - `.gitignore` — исключает `.venv`, `.env`, `__pycache__` и т.д.
- Проверка работоспособности: `manage.py check` без ошибок, миграции применяются, `runserver` отвечает HTTP 200 на `/`.
- Задача «Инициализировать репозиторий...» отмечена `[x]` в TASKS.md.

**Не сделано / отложено:** PostgreSQL+PostGIS, хостинг, настоящие env-переменные, i18n-инфраструктура, бренд-конфиг — следующие задачи Этапа 0.
**Заметки для следующей сессии:** Запуск dev-сервера: `backend/.venv/bin/python backend/manage.py runserver` из корня проекта. База по умолчанию sqlite для локальной разработки; Postgres настраивать в следующей задаче. `psycopg2-binary==2.9.11` уже в requirements. Дизайн-референс — `tajikistan-map-3d.html` (индиго `#1a2740` + охра `#c98a2c`, шрифты Fraunces/Manrope).

---

## Сессия 0 — (дата создания проекта)
**План:** —
**Сделано:** Создан комплект документов проекта (PROJECT.md, TASKS.md, PROGRESS.md, DECISIONS.md, ISSUES.md, OPENCODE.md) на основе брейншторма с основателем. Есть рабочий HTML-прототип карты (2D и 3D) на MapTiler — использовать как визуальный референс дизайна (индиго + охра, шрифты Fraunces/Manrope).
**Не сделано / отложено:** Само приложение ещё не начато.
**Заметки для следующей сессии:** Начинать с Этапа 0 в TASKS.md. MapTiler API-ключ передаётся отдельно, не хранить в открытом репозитории.
