"""Лёгкая модерация контента по списку запрещённых слов (PROJECT.md раздел 10).

MVP: публикация контента волонтёров проверяется автоматически по словникам.
Список ниже — черновой базовый набор, подлежит утверждению основателем
(см. ISSUES.md). Полноценная ИИ-модерация — отдельная задача после 1000
пользователей, здесь не используется.

Поиск — подстрока (case-insensitive), а не целые слова: ловит словоформы
(«грабёж» в «грабежами»). Это даёт редкие ложные срабатывания (например,
англ. "kill" внутри "skill") — приемлемо для MVP и будет уточнено, когда
основатель утвердит финальный список слов.
"""

# Черновой базовый список. Основатели могут править свободно:
# формат — {языковой код: [слова, ...]}. Слова приводятся к нижнему регистру.
FORBIDDEN_WORDS = {
    "ru": ["убей", "убить", "грабёж", "грабеж", "наркотик", "террор", "теракт", "обман", "лохотрон", "дурак", "мошенник"],
    "en": ["kill", "murder", "kidnap", "rape", "terror", "bomb", "scam", "fraud"],
    "tg": ["кушт", "террор", "дуздӣ", "фиреб", "нашъа", "куштан"],
}


def find_forbidden_words(text, lang):
    """Возвращает список запрещённых слов (уникальных), найденных в тексте."""
    if not text:
        return []
    lowered = text.casefold()
    found = [word for word in FORBIDDEN_WORDS.get(lang, []) if word in lowered]
    return sorted(set(found))


def check_place(place):
    """Проверяет мультиязычные поля места.

    Возвращает список {lang, word} совпадений — пустой, если всё чисто.
    """
    hits = []
    for lang in ("ru", "en", "tg"):
        name = getattr(place, f"name_{lang}", "") or ""
        description = getattr(place, f"description_{lang}", "") or ""
        for text in (name, description):
            for word in find_forbidden_words(text, lang):
                hits.append({"lang": lang, "word": word})
    return hits