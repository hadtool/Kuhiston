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

## Сессия 14 — 2026-09-15
**План:**
- Этап 6 «Офлайн-режим» (PROJECT.md раздел 8): 1) скачивание тайлов карты по выбранному региону (офлайн-кэш), 2) скачивание данных о местах по региону в локальное хранилище, 3) индикатор «доступно офлайн» в интерфейсе.

**Сделано:**
- Backend (API офлайн-бандлов):
  - `RegionSerializer` в `places/serializers.py` — id/code/name (на языке запроса)/places_count (только опубликованные).
  - `OfflineRegionsView` (`GET /api/offline/regions/`) — список регионов для скачивания.
  - `OfflineRegionBundleView` (`GET /api/offline/regions/<pk>/`) — `{region, bounds:{lat/lng min/max из мест}, count, places[]}`; места — полные `PlaceDetailSerializer` (название/описание на языке запроса, категория, координаты, фото, рейтинг); для пустого региона `bounds: null`. 404 для несуществующего pk.
  - URL добавлены в `backend/kuhiston/urls.py`.
- Фронтенд (`frontend/templates/home.html`, `frontend/static/js/map.js`, `frontend/static/css/map.css`):
  - Кнопка `#btn-offline` (📶) в панели действий; панель `#offline-panel` — список регионов с количеством мест и кнопкой «Скачать» (после скачивания — «Удалить»).
  - `downloadRegion()` — выборка бандла в localStorage (`kuh.offline.v1.<code>`), затем `precacheRegionTiles()` — тайлы MapTiler (`streets-v2/{z}/{x}/{y}.png?key=`) в Cache API по bbox региона для zoom 5/8/10.
  - `offlineSaved()/offlineCachedPlaces()` — чтение кэша; фолбэк: при падении `/api/places/` рендерятся маркеры из кэша, при падении `/api/places/<id>/` карточка места открывается из кэша.
  - Индикатор: бейдж `#offline-badge` «Доступно офлайн: <регионы>» + блок `#offline-cache-info` со списком скачанных регионов; слушатели `online`/`offline` перезагружают места.
  - Service worker `frontend/static/js/sw.js` (кэш shell `kuhiston-shell-v1`: base.css/map.css/map.js, кэширование статики same-origin, тайлы maptiler отдаются из Cache API при наличии), регистрируется из map.js.
  - Стили `.offline-cache-info`, `#offline-badge`, `.btn.small/.ochre/.ghost` в map.css.
- Новые ключи `js_strings` (offline_btn, offline_hint, offline_download, offline_downloading, offline_saved_ok, offline_remove, offline_cached, offline_empty, offline_places) + переводы 9 строк (ru — identity, en/tg переведены), fuzzy-флаги сняты, `compilemessages` выполнен.
- Проверено тест-клиентом (sqlite): `/api/offline/regions/` = 200 (массив с name/places_count, язык переключается), бандл = 200 (region/bounds/count/places, пустой регион → bounds null, 404 для чужого pk), `/` рендерится и содержит `btn-offline`, `offline-panel`, `offline-badge` и все ключи офлайн в js_strings. `manage.py check` (0 silenced) и `makemigrations --check` без изменений.

**Не сделано / отложено:**
- Живое скачивание тайлов/офлайн-карты в браузере не проверить (нет браузера и сети MapTiler с ключом); сетевой код (precacheRegionTiles, sw.js) проверен только чтением. Проверка у основателя в браузере с реальным ключом.
- Фотографии для офлайна: кэшируются исходные URL бандла, сжатые версии для офлайн-кэша (PROJECT.md 8.3) — как отдельная задача, не была в TASKS.

**Заметки для следующей сессии:**
- Этап 6 закрыт (3/3). Осталось: Этап 0 (PostGIS, блокер машины основателя), Этап 7 «Монетизация» (2 задачи: платное продвижение — админ включает вручную; кнопка/страница донатов).
- Офлайн-данные лежат в localStorage под `kuh.offline.v1.*`; тайлы — Cache API `kuh.tiles.<code>`; shell — `kuhiston-shell-v1`.
- Коммит Этапа 6 — `08a088a`.

---

## Сессия 10 — 2026-09-14
**План:**
- Этап 2, задача 1: «Интеграция MapTiler на фронтенде (2D режим, живой стиль)» — PROJECT.md раздел 9.
- Создать view главной страницы (карта), шаблон `home.html` на базе `base.html`, статику (css/js). Инициализация MapTiler SDK JS (MapLibre-основа, тут же задел под 3D-террейн из следующей задачи) со стилем Streets и API-ключом из настроек (не в коде).
- Проверить: страница рендерится (GET 200), ключ и скрипты подставляются, язык интерфейса переключается.
- Задача 2: «Определение местоположения пользователя + ручной выбор точки» — кнопка геолокации и клик по карте для выбора точки (2D).

**Сделано:**
- Весь Этап 2 (задачи 1–5): страница-карта, геолокация + ручная точка, ближайшие места с фильтром по категориям, карточка места, 3D-рельеф.
- Фронтенд: `frontend/templates/home.html` (extends base.html; `<div id="map">` с `data-maptiler-key` из `settings.MAPTILER_API_KEY`; чипы категорий; кнопки «локация» и «3D-рельеф»; подсказка точки; сайдбар-карточка; `js_strings|json_script:"i18n-strings"`; MapTiler SDK UMD 1.2.0 с jsdelivr — ключ не хардкодится); `frontend/static/css/map.css` (палитра индиго+охра, чипы, сцены, карточка, маркер `.place-dot`); `frontend/static/js/map.js` (init `maptilersdk.MapStyle.STREETS`; `loadGeolocate`; ручной выбор точки кликом; `loadPlaces` с фильтром категории; `openPlaceCard`; `toggle3D` через `setTerrain`/exaggeration; парсинг i18n-строк; `formatRating`/`escapeHtml`).
- Backend: `places/views.py::home` — отдаёт ключ, категории и `js_strings` на активном языке; `place-dot`-маркер и стили; `backend/kuhiston/settings.py`: разрешён `testserver` в ALLOWED_HOSTS в DEBUG.
- API (нужно для задач 3–4): `backend/places/api.py` — `PlaceListView` (`/api/places/`: только `published`, фильтр `?category=<code>`, сортировка haversine по `?lat&lng`, `distance_km`, рейтинг), `PlaceDetailView` (`/api/places/<id>/`: все поля на языке запроса, `photos[]` с абсолютными URL, средний рейтинг, `reviews_count`, `distance_km`), `CategoryListView` (`/api/categories/`); `backend/places/serializers.py` (список/деталь/категория/фото, языки через контекст); маршруты в `backend/kuhiston/urls.py`.
- Проверено (Postgres, опубликованы демо-места 1,2,3,4,5,6,8): `GET /` = 200, есть `id="map"`, `data-maptiler-key`, чипы; `/api/places/` = 200 (7 мест), сортировка по расстоянию корректна, фильтр по категории работает; `/api/places/<id>/` = 200 (все поля, photos, reviews_count). Языки: чипы и js_strings переключаются ru/en/tg (EN: «Find my location», TG: «Ҷойи манро муайян кун»).
- Переводы: добавлены 16 строк home.html + js_strings в `frontend/locale/{ru,en,tg}` (ru — как есть, en/tg переведены), `compilemessages` выполнен. Нюанс: `makemessages` сканирует только текущий каталог — запускать из корня проекта с `--extension html --extension py`, чтобы попадали и Python-строки views.py.
- Исправлен баг DRF: поле `reviews_count` с `source='reviews_count'` — AssertionError (redundant source), убрано явное объявление (маппится на property модели).
- `manage.py check` (обе БД, 0 silenced), `makemigrations --check` без изменений.

**Не сделано / отложено:**
- Живой рендер карты и 3D в браузере и реальную геолокацию в песочнице не проверить (нет браузера) — проверено: разметка, статусы API, наличие ключа. Для живой карты нужен настоящий `MAPTILER_API_KEY` от основателя (ISSUES открыта).

**Заметки для следующей сессии:**
- Этап 2 закрыт полностью (5/5). Дальше — Этап 3 «Маршруты»: простые маршруты (список/показ N ближайших точек), готовые многодневные маршруты (модель данных + отображение по дням), навигация по дорогам/тропам (роутинг-движок OSRM — см. ISSUES).
- Проверки: sqlite (`DATABASE_URL=`) или Postgres (`DATABASE_URL=postgres://postgres@127.0.0.1:5432/kuhiston`), Postgres запущен в `/tmp/opencode/pgdata`. Демо-места опубликованы (1,2,3,4,5,6,8) — API отдаёт их.
- API-эндпоинты карты: `/api/places/` (+ `?lat&lng&category`), `/api/places/<id>/`, `/api/categories/`.

---

## Сессия 12 — 2026-09-15
**План:**
- Этап 4 «Бронирование» (PROJECT.md раздел 7): форма заявки, кабинет владельца (подтверждение/отклонение), пометка «оплата на месте», регистрация/вход туриста.

**Сделано:**
- `backend/booking/forms.py` — `BookingRequestForm` (tourist_name, tourist_contact, check_in/check_out, notes, pay_on_site; валидация: выезд не раньше заезда; переводные метки/подсказки).
- `backend/booking/views.py` — `object_list` (активные объекты, фильтр `?place=<id>` по M2M мест, `?category`), `object_detail` (карточка + POST-заявка, tourист привязывается если залогинен), `my_panel` (кабинет владельца: свои объекты + заявки), `set_status` (confirm/reject с проверкой владельца).
- `backend/booking/urls.py` (`app_name="booking"`): `/booking/`, `/booking/object/<pk>/`, `/booking/my/`, `/booking/my/<pk>/<status>/`. Подключён в корневой `urls.py` (`path('booking/', include('booking.urls'))`).
- Шаблоны `frontend/templates/booking/{objects,object_detail,my_panel}.html` (extends base.html, `page.css`, таблица заявок с кнопками Подтвердить/Отклонить, бейдж «оплата на месте» 💵).
- Авторизация туриста: `backend/users/forms.py::TouristSignupForm` (UserCreationForm на кастомную модель), `backend/users/views.py` (signup/login/logout), `backend/users/urls.py` (`/users/signup/ /login/ /logout/`, app_name="users"), шаблоны `frontend/templates/registration/{signup,login}.html`. Nav-ссылки (Карта/Бронирование/Кабинет/Вход/Регистрация/Выйти) добавлены в шапку `base.html`, стили — `frontend/static/css/base.css` (+ `.site-nav` в map.css).
- Локализация мультиязычных имён в шаблонах: новый templatetag `users/templatetags/localize.py` (`get_name`/`get_description` фильтры с аргументом-языком; методы с аргументами в шаблонах Django не вызываются) — `{{ obj|get_name:LANGUAGE_CODE }}`.
- Кнопка «Забронировать рядом» в карточке места (map.js → `/booking/?place=<id>`), флаг `book_btn` в `js_strings` (places/views.py).
- Переводы: 39 новых строк для Этапа 4 в `frontend/locale/{ru,en,tg}` (ru — identity, en/tg переведены), `compilemessages`.
- Проверено тест-клиентом на sqlite (Postgres в песочнице перестал подниматься — см. ISSUES): list/detail/my_panel = 200, POST заявки = 302 с redirect, pay_on_site/status сохранены, валидация дат не создаёт запись, confirm/reject меняют статус, signup → авторизован, login/logout работают, home = 200. Все 12 проверок прошли.

**Не сделано / отложено:**
- Живой рендер новых страниц в браузере не проверялся (нет браузера).
- Замечание: наша локальная Postgres-БД в песочнице больше не поднимается (удалён бинарь); демо-проверки переведены на sqlite. PostGIS-проверка всё ещё требует машины основателя.

**Заметки для следующей сессии:**
- Этап 4 закрыт (4/4). Дальше — Этап 5 «Отзывы»: форма отзыва/оценки после регистрации + отображение рейтинга и отзывов на карточке места. Модель Review уже есть (Этап 1), рейтинг уже считается в API (`rating`, `reviews_count`).
- Нужно закоммитить Этап 4 (не сделан в этой сессии — коммит `?`), обновить First commits список.
- Изменено: templatetag лежит в `users/templatetags/localize.py` (не в kuhiston — он не в INSTALLED_APPS).

---

## Сессия 13 — 2026-09-15
**План:**
- Этап 5 «Отзывы» (PROJECT.md раздел 8): 1) форма отзыва/оценки после регистрации, 2) отображение рейтинга и отзывов на карточке места.

**Сделано:**
- Backend: `ReviewSerializer` (id, author=username, rating, text, created_at) в `places/serializers.py`; `PlaceReviewsView` в `places/api.py`:
  - `GET /api/places/<pk>/reviews/` — для опубликованного места: `{average, count, reviews[], my_review}`; средний из `Place.average_rating`/`reviews_count` (уже были в Этапе 2);
  - `POST` — требует auth (иначе 401), `rating` 1–5 (иначе 400), `update_or_create` по (place, author) — повторный отзыв пользователя обновляется, ответ 201.
  - URL: `path('api/places/<int:pk>/reviews/')`.
- Фронтенд (`map.js`): в карточке места блок `#card-reviews`; `loadReviews`/`renderReviews` — суммарный рейтинг, список отзывов (автор, звёзды, дата, текст), форма отзыва для авторизованных (звёзды 1–5 кликом + textarea + кнопка; редактирование своего отзыва: презаполнена из `my_review`), для гостей — ссылка «Войдите, чтобы оставить отзыв»; `postReview` через `fetch` POST с `X-CSRFToken` из cookie; `getCsrfToken`. Признак `data-auth` на `#map-page` (`request.user.is_authenticated`) в `home.html`.
- Новые ключи `js_strings` (reviews_title, reviews_empty, review_yours, review_leave, review_rating_label, review_text_placeholder, review_submit, review_logged_in_need, review_saved, review_fail) в `places/views.py`; стили отзывов в `map.css`.
- Переводы: 10 новых строк Этапа 5 в `frontend/locale/{ru,en,tg}` (сняты fuzzy-флаги у «Оставить отзыв»/«Отправить отзыв»/«Не удалось сохранить отзыв»), `compilemessages`.
- Проверено тест-клиентом (sqlite): GET пустой = 200 `{average:null,count:0}`; POST аноним = 401; POST авторизован = 201; повторный POST обновляет (count=1, rating 5→4, avg обновляется); rating=9 = 400; home = 200 и содержит ключи отзывов. `manage.py check` и `makemigrations --check` чистые. JS-проверка `node --check` невозможна (node отсутствует) — код прочитан вручную.

**Не сделано / отложено:**
- Живой рендер/отправку отзыва в браузере не проверить (нет браузера, node); верификация — только тест-клиент и чтение JS.
- `review_rating_label` («Оценка») в JS пока не используется (звёзды кликабельны без подписи поля) — ключ переведён для будущего использования.

**Заметки для следующей сессии:**
- Этап 5 закрыт (2/2). Осталось: Этап 0 (PostGIS, блочер машины основателя), Этап 6 «Офлайн-режим» (3 задачи), Этап 7 «Монетизация» (2 задачи).
- Модель `Review` с полями и constraint `review_rating_range` создана на Этапе 1 и уже в миграциях—новых миграций не потребовалось.
- Коммит Этапа 5 — `?` (дописать хеш в следующей сессии).

---

## Сессия 11 — 2026-09-14
**План:**
- Задачи Этапа 3 «Маршруты» (PROJECT.md раздел 6):
  1. Простые маршруты — список/показ N ближайших точек.
  2. Готовые многодневные маршруты (модель данных + отображение по дням).
  3. Навигация по дорогам/тропам (роутинг-движок OSM — см. ISSUES про выбор OSRM).

**Сделано (задача 1 «Простые маршруты: N ближайших точек»):**
- `backend/places/api.py::SimpleRouteView` (`GET /api/route/simple/?lat=..&lng=..&limit=N`): расстояние по хаверсину от старта, сортировка, leg-расстояние между соседними точками, `total_km`; `limit` 1–10 (по умолчанию 5); 400 без/с некорректными координатами.
- `backend/places/serializers.py::SimpleRoutePointSerializer` — id/name/category/lat/lng/distance_from_start_km/leg_km (динамические поля через `SerializerMethodField`, иначе DRF строит поле из модели и падает).
- Фронтенд: кнопка `#btn-route` в `home.html`, панель `#route-panel` (список стопов с № и дистанцией, клик по стопу открывает карточку места), полилиния через `map.addSource/addLayer` в `map.js` (индиго, dash), стили в `map.css`.
- Исправлен баг Этапа 2 в `map.js`: API `/api/places/` отдаёт массив, а код ждал `data.places` — маркеры не рисовались. Теперь `renderMarkers(data || [])`.
- Переводы: 6 строк (Маршрут, Ближайшие места, Итого, «Кликните по точке…», «Рядом не найдено мест», км) в ru/en/tg, `.mo` скомпилированы.
- Проверено на Postgres: `/api/route/simple/?lat=38.58&lng=68.78&limit=3` → 200 (count=3, total_km, отсортировано, leg-дистанции логичны); 400 без координат и с нечисловыми; limit зажат до 10; `/` рендерится с `btn-route` и `route-panel`; `/api/places/` не сломан. `manage.py check` (обе БД) и `makemigrations --check` без изменений.

**Сделано (задача 2 «Готовые многодневные маршруты»):**
- Новое приложение `backend/routes`: модель `Route` (название/описание на 3 языках, регион, `duration_days`, автор, `moderation_status`, `is_promoted`, timestamps; методы `get_name/get_description`, свойства `stops_count` и `total_km` по хаверсину) + `RouteStop` (route FK, place FK, `day`, `order`, `minutes`, `note`; сортировка по дню/порядку).
- `backend/places/models.py::Place.distance_to(other)` — хаверсин-расстояние между местами (используется `Route.total_km`).
- Админка: `RouteAdmin` (инлайн `RouteStop`, статус модерации/продвижение редактируются из списка, авто `author`, модерация по запрещённым словам через `kuhiston/moderation.check_route`) + `RouteStopAdmin` (с автокомплитами).
- API: `GET /api/routes/` (опубликованные, заголовки на языке запроса, `stops_count`, регион; фильтр `?region=<code>`), `GET /api/routes/<id>/` (дни → стопы с местом: координаты, категория, тайминг, заметка).
- Фронтенд: кнопка `#btn-routes` (🎒) и панель `#routes-panel` — список маршрутов; при клике — «маршрут по дням» (дни → стопы), полилиния охрой, клик по стопу открывает карточку места.
- Миграция `routes.0001_initial` применена на sqlite и Postgres. Проверено на Postgres: маршрут «Горы Фана — 3 дня» с 4 стопами отдаётся списком и деталью (4 дня); `check_route` ловит «грабёж» в названии. `manage.py check`/`makemigrations --check` чисто.
- Переводы: 5 строк (Готовые маршруты, дн., точек, День, мин) в ru/en/tg.

**Не сделано / отложено:**
- Задача 3 (навигация по дорогам/тропам через OSRM) Этапа 3 — следующая сессия; выбор OSRM vs готовый сервис — открытый вопрос ISSUES.

**Сделано (задача 3 «Навигация по дорогам/тропам (OSRM)»):**
- Решение в DECISIONS.md: на MVP — публичный OSRM-демо-сервер (`router.project-osrm.org`, данные OSM) через серверный прокси (нет CORS/ключей у фронта); при недоступности — автоматический фолбэк по прямой (хаверсин × 1.3). Self-hosted OSRM (docker + OSM по Таджикистану) — продакшн-задача на машине основателя (зафиксировано в ISSUES.md).
- `backend/kuhiston/routing.py::osrm_route(start, end, profile)` (driving/foot/bike, urllib без requests, таймаут 6с): возвращает distance_km/duration_min/geometry(GeoJSON)/source("osrm"|"fallback"); никогда не бросает исключений.
- `backend/places/api.py::NavigationRouteView` — `GET /api/route/navigation/?start=lat,lng&end=lat,lng&profile=driving` (400 без/с битыми координатами).
- Фронтенд: кнопка «🚗 Построить маршрут» в карточке места (`#card-nav`) → полилиния маршрута (индиго) + панель `#nav-panel` с дистанцией/временем и пометкой «маршрут по прямой» при фолбэке.
- Проверено на Postgres: `/api/route/navigation/` возвращает OSRM-маршрут (source: osrm, 7.0 км, 12 мин) — сеть из песочницы доступна; 400 для пустых/битых координат; `/` рендерится с `nav-panel`. `manage.py check`/`makemigrations --check` чисто. Переводы 3 новых строк в ru/en/tg.

**Сделано (задачи 1–3 Этапа 3):** Этап 3 закрыт полностью.

**Заметки для следующей сессии:**
- В `api.py` рядом с generics-вьюхами теперь есть `APIView` — аккуратно с импортами.
- Полилиния маршрута пересоздаёт source/layer при повторном построении (уже обработано в `renderRoute`). 

---

## Сессия 9 — 2026-09-14
**План:**
- Задача Этапа 1: «Лёгкая модерация: список запрещённых слов (ru/en/tg), статус "на проверке/опубликовано/отклонено"».
- Создать список запрещённых слов (ru/en/tg) в отдельном модуле `moderation.py`.
- При сохранении места волонтёром: автоматическая проверка текста и проставление статуса `rejected` если найдены запрещённые слова.
- Обновить TASKS.md, закоммитить.

**Сделано:**
- Модуль `kuhiston/moderation.py`: черновой список `FORBIDDEN_WORDS` на ru/en/tg, `find_forbidden_words(text, lang)` (подстрока, без регистра — ловит «грабёж» в «грабежами») и `check_place(place)` — проверяет название+описание на трёх языках.
- `PlaceAdmin.save_model`: если найдено хоть одно запрещённое слово → `moderation_status = rejected` (даже если формально пытались поставить `published`). Чистое место остаётся `pending`.
- Проверено на Postgres через тест-клиент: чистое место = `pending`, место с «грабёж на дороге» = `rejected` (независимо от запрошенного статуса).
- `manage.py check` (обе БД, 0 silenced), `makemigrations --check` без изменений. Этап 1 полностью закрыт.

**Не сделано / отложено:**
- Финальный список запрещённых слов — задача основателя (черновик в модуле, ISSUES открыта).
- Модерация отзывов (в PROJECT.md не требуется на MVP — отзывы модерируются вручную при необходимости).

**Заметки для следующей сессии:**
- Этап 1 закрыт полностью (6/6 задач). Дальше — **Этап 2 «Карта и просмотр мест»**: интеграция MapTiler на фронтенде (2D, живой стиль), геолокация, показ ближайших мест, карточка места, 3D-режим.
- Проверки можно гонять: sqlite (`DATABASE_URL=` пустой) или Postgres (`DATABASE_URL=postgres://postgres@127.0.0.1:5432/kuhiston`). Postgres 17.11 запущен в `/tmp/opencode/pgdata` (bin в `/tmp/opencode/pg17`). 

---

## Сессия 8 — 2026-09-14
**План:**
- Задача Этапа 1: «Веб-панель для волонтёров: логин/пароль, форма добавления места».
- По DECISIONS.md панель волонтёра = Django-админка, ограниченная ролью: группа «Волонтёр» + права (добавление/изменение мест и фото, просмотр категорий/регионов), без доступа к пользователям/бронированиям/модерации.
- Настроить группу через data-migration (иденmпотентно), чтобы применилась на любой БД автоматически.
- Проверить тест-клиентом Django: логин волонтёра, добавление места через админку (POST), запрет доступа к чужим разделам.
- Обновить TASKS.md/DECISIONS.md/PROGRESS.md, закоммитить.

**Сделано:**
- Data-migration `users.0002_volunteer_group`: создание группы «Волонтёр» с правами add/change/view Place + PlacePhoto, view PlaceCategory + Region. Идемпотентна (get_or_create), выполняется на любой БД автоматически.
- `PlaceAdmin.save_model`: при создании нового места автоматически проставляет `added_by = request.user` (если не задан).
- Проверено тест-клиентом Django (Postgres): волонтёр (`is_staff=True`, группа) может зайти в админку, добавить место через POST (csrf, management-form для инлайнов — префикс `photos`). Место создаётся с `added_by = vol_test` и `moderation_status = pending`. Доступ к `/admin/users/user/`, `/admin/booking/`, удалению мест — запрещён (403 Forbidden, `PermissionDenied`).
- Нюанс: CSRF-токен обязателен для POST; инлайн PlacePhoto использует префикс `photos` (от `related_name`); management-form без пустых строк инлайна (TOTAL_FORMS=0) позволяет пропустить инлайн при добавлении.
- `manage.py check` (обе БД, 0 silenced), `makemigrations --check` без изменений.

**Не сделано / отложено:**
- «Лёгкая модерация: список запрещённых слов» — следующая задача (Etап 1).

**Заметки для следующей сессии:**
- Волонтёрская веб-панель готова: волонтёр добавляет места через Django admin, `added_by` проставляется, статус `pending`. Модерация проверяется при публикации — следующая задача: проверка текста по списку запрещённых слов перед сменой статуса.
- Инлайн-формы: префикс берётся из `related_name` модели (PlacePhoto → `photos`, Review → `review`), MANAGEMENT_FORM обязательна даже если строк нет. 

---

## Сессия 7 — 2026-09-14
**План:**
- Задача Этапа 1: «Модель "Отзыв/рейтинг"».
- Модель `Review`: FK на место, автор (турист, `AUTH_USER_MODEL`), оценка 1–5, текст, timestamps; свойство среднего рейтинга и количества отзывов на `Place`.
- Админка (список с фильтром по оценке/месту, инлайн на месте), миграции на sqlite и Postgres, проверка расчёта рейтинга.
- Обновить TASKS.md/DECISIONS.md/PROGRESS.md, закоммитить.

**Сделано:**
- `Review` в `places/models.py`: FK на место (CASCADE, `related_name='reviews'`), автор (`AUTH_USER_MODEL`, SET_NULL), оценка 1–5 (+ валидаторы и `CheckConstraint` в БД), текст, timestamps. На `Place` добавлены свойства `average_rating` и `reviews_count`.
- Админка: список отзывов (фильтры по оценке/дате, редактирование оценки из списка, поиск), инлайн на странице места.
- Миграция `places.0002_review` применена на sqlite и реальном Postgres.
- Проверено на Postgres: средний рейтинг 4.5 для [5,4], обратные связи и подсчёт работают; попытка создать оценку 6 отклоняется `IntegrityError` (CheckConstraint).
- Нюанс Django 6.1: у `CheckConstraint` параметр называется `condition=` (не `check=`).
- `manage.py check` (обе БД, 0 silenced), `makemigrations --check` без изменений.

**Не сделано / отложено:**
- «Веб-панель для волонтёров: логин/пароль, форма добавления места» — следующая задача Этапа 1.
- «Лёгкая модерация (запрещённые слова)» — далее.

**Заметки для следующей сессии:**
- Волонтёрская панель: кастомный User с ролью `volunteer` уже есть; панель можно делать на базе Django admin (ограничить права через группы) или отдельными view. Уточнить у основателя формат: админка Django или свой интерфейс. 

---

## Сессия 6 — 2026-09-14
**План:**
- Задача Этапа 1: «Модель "Заявка на бронирование"» (PROJECT.md раздел 7): заявка без онлайн-оплаты, подтверждение владельцем.
- Модель `BookingRequest` в приложении `booking`: FK на объект бронирования, турист (пользователь) + контактные данные снимком, даты, комментарий, «оплата на месте», статус.
- Админка (список, фильтры по статусу), миграции на sqlite и Postgres, проверка связей и переходов статуса.
- Обновить TASKS.md/DECISIONS.md/PROGRESS.md, закоммитить.

**Сделано:**
- `BookingRequest` в `booking/models.py`: FK на `BookingObject` (CASCADE, `related_name='requests'`), FK на туриста (`AUTH_USER_MODEL`, SET_NULL) + снимок `tourist_name`/`tourist_contact`, даты заезда/выезда, `notes`, `pay_on_site`, статус `new/confirmed/rejected/cancelled`.
- Админка: список с редактируемым статусом, фильтры по статусу/оплате, поиск, автокомплит туриста, инлайн на странице объекта, readonly timestamps.
- Миграция `booking.0002_bookingrequest` применена на sqlite и реальном Postgres.
- Проверено на Postgres: заявка создаётся, статус переходит `new → confirmed`, обратные связи (объект→заявки, турист→заявки) и фильтрация по статусу работают.
- `manage.py check` (обе БД, 0 silenced), `makemigrations --check` без изменений.

**Не сделано / отложено:**
- Модель «Отзыв/рейтинг» — следующая задача Этапа 1.
- Форма заявки, личный кабинет владельца, регистрация туриста — Этап 4 (сейчас только схема данных).

**Заметки для следующей сессии:**
- Для «Отзыва»: FK на место + FK на туриста (`AUTH_USER_MODEL`), оценка (1–5), текст на 3 языка (или один текст), обратная связь с рейтингом места. 

---

## Сессия 5 — 2026-09-14
**План:**
- Задача Этапа 1: «Модель "Объект для бронирования" (жильё/гид/транспорт/ресторан) со связью к местам» из PROJECT.md раздел 7.
- Создать приложение `booking`: категория объекта бронирования (расширяемая), объект (название/описание на 3 языках, координаты, регион, владелец-пользователь, контакты, признак продвижения), M2M-связь с местами.
- Зарегистрировать в админке, применить миграции на sqlite и реальном Postgres, проверить связи (объект↔места, объект↔владелец).
- Обновить TASKS.md/DECISIONS.md/PROGRESS.md, закоммитить.

**Сделано:**
- Приложение `booking`: `BookingCategory` (расширяемые категории жильё/гид/транспорт/ресторан, названия на 3 языках) и `BookingObject` (название/описание на 3 языках, координаты lat/lng, регион, владелец-FK на `AUTH_USER_MODEL`, контакты phone/email/website, `is_active`, `is_promoted`) с M2M-связью `places` → `Place`.
- Админка: категория + объект (фильтры по категории/региону/активности/продвижению, `filter_horizontal` для мест, fieldsets).
- Миграция `booking.0001_initial` применена на sqlite и реальном Postgres.
- Проверено на Postgres: гостевой дом связан с двумя местами через M2M, обратные связи работают (место→объекты, владелец→объекты, категория→объекты), дефолты `is_active/is_promoted`, сортировка с продвижением.
- `manage.py check` (обе БД, 0 silenced), `makemigrations --check` без изменений.
- Заметно: `BookingRequest` НЕ включён в эту сессию — это следующая задача в TASKS.md (не смешивать задачи). `related_name='objects'` вызывает ошибку E348 (конфликт с менеджером) — использовать `booking_objects`.

**Не сделано / отложено:**
- Модель «Заявка на бронирование» — следующая задача Этапа 1.
- Модель «Отзыв/рейтинг» — далее.

**Заметки для следующей сессии:**
- Для «Заявки» общая логика: FK на BookingObject, статус (новая/подтверждена/отклонена/отменена), даты заезда/выезда, «оплата на месте», контакты туриста — ТЗ в PROJECT.md раздел 7. 

---

## Сессия 4 — 2026-09-14
**План:**
- Задача Этапа 1: «Модель "Пользователь" с ролями (турист/волонтёр/владелец места/админ)».
- Создать кастомную модель пользователя `users.User` (`AUTH_USER_MODEL`), пока на других моделях нет необратимых внешних ключей на User. Перенести FK `Place.added_by` на `settings.AUTH_USER_MODEL`.
- Учесть, что миграции auth/places уже применены: после смены `AUTH_USER_MODEL` пересоздать базы с нуля (ранняя разработка — допустимо).
- Проверить на sqlite и реальном Postgres: миграции, создание пользователей всех ролей, FK из места на волонтёра.
- Обновить TASKS.md/DECISIONS.md/PROGRESS.md, закоммитить.

**Сделано:**
- Создано приложение `users`: кастомная модель `User` (AbstractUser) с полем `role` (tourist/volunteer/place_owner/admin), хелперы `is_volunteer()/is_place_owner()/is_admin()`, админка с колонкой «роль» (`backend/users/models.py`, `users/admin.py`).
- `settings.py`: `AUTH_USER_MODEL = 'users.User'`, `users` в INSTALLED_APPS; `Place.added_by` переведён на `settings.AUTH_USER_MODEL` (создана миграция `places.0002`).
- Так как auth-миграции уже были применены со стандартным User, обе БД пересозданы с нуля (sqlite и Postgres 17.11) — на этой стадии это схема, не данные.
- Проверено на реальном Postgres: `users.User` в качестве AUTH_USER_MODEL; созданы пользователи всех 4 ролей; `is_*`-хелперы работают; FK места на волонтёра создаётся, обратный `user.added_places` и фильтрация `Place.objects.filter(added_by=...)` работают.
- `manage.py check` (sqlite и Postgres, 0 silenced), `makemigrations --check` без изменений.

**Не сделано / отложено:**
- Следующие модели Этапа 1 (объект для бронирования, заявка, отзыв) — следующие сессии.
- Волонтёрская веб-панель, регистрация/вход — отдельные задачи Этапа 1/4.

**Заметки для следующей сессии:**
- Кастомный User уже стоит — новые FK на пользователя делать через `settings.AUTH_USER_MODEL`.
- Роли в BaseUserAdmin для поля role — готово. При добавлении полномочий волонтёрам можно опираться на группы Django, но для MVP достаточно поля `role`. 

---

## Сессия 3 — 2026-09-14
**План:**
- Этап 0 остался один незакрытый пункт «PostGIS-проверка» — он заблокирован внешне (нужна машина основателя с docker или Neon-БД), поэтому перехожу к Этапу 1 как к независимой работе над моделями.
- Модель «Место» (все поля из PROJECT.md раздел 5) + зависимые модели «Регион» и категория/фото.
- Решить, как хранить координаты/мультиязычные поля — записать в DECISIONS.md.
- Проверить: makemigrations/migrate реально работают, объекты создаются и читаются.

**Сделано:**
- Создано приложение `places` с моделями: `Region`, `PlaceCategory`, `Place`, `PlacePhoto` (`backend/places/models.py`) — все поля «Места» из раздела 5 PROJECT.md (название/описание на 3 языках, категория, координаты, регион, фото, часы работы, входная цена, сложность доступа, сезонность, статус модерации, кто добавил).
- Решения зафиксированы в DECISIONS.md: координаты — два `DecimalField` (lat/lng), а не `PointField` (иначе нужны GEOS/GDAL, ограничение из Этапа 0); мультиязычные поля — отдельные колонки на язык; категория — отдельная модель.
- Админка: `backend/places/admin.py` — регистрация всех моделей, инлайн-фото, фильтры/поиск/поля модерации.
- MEDIA (фото): `MEDIA_URL/MEDIA_ROOT`, раздача в dev, добавлен `Pillow==12.3.0` в requirements.
- Проверено на двух БД:
  - sqlite (песочница): миграции + создание/чтение региона, категории, места, фото (все 3 языка, координаты, сезоны);
  - реальный PostgreSQL 17.11 (портативные бинарники в `/tmp/opencode/pg17`, БД `kuhiston`): миграции применены, объект «Озеро Кули Калон» создан и считан через `select_related`.
- `manage.py check` (0 silenced) и `makemigrations --check` без изменений.

**Не сделано / отложено:**
- Модели «Пользователь с ролями», «Объект для бронирования», «Заявка», «Отзыв» — следующие задачи Этапа 1.
- Проверка `PointField`/PostGIS-индексов — по-прежнему требует машины с GEOS/GDAL (не в песочнице).

**Заметки для следующей сессии:**
- Postgres-сервер для проверки поднимается так: `/tmp/opencode/pg17/bin/initdb -D /tmp/opencode/pgdata -U postgres -A trust --no-locale -E UTF8`; затем `pg_ctl start -o "-p 5432 -h 127.0.0.1"`; БД создаётся через psycopg2 (в поставке нет `psql`). `DATABASE_URL=postgres://postgres@127.0.0.1:5432/kuhiston`.
- Следующая задача Этапа 1: «Модель „Пользователь" с ролями» — расширять `AUTH_USER_MODEL` до того, как появятся внешние ключи на User в других моделях.
- Для sqlite-режима миграции тоже применяются — проверки можно гонять без Postgres. 

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
