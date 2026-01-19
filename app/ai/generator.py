from app.models import NewItem
from app.ai.openai_client import generate_text

def build_prompt(item: NewItem) -> str:
    raw = item.raw_text or ""
    return f"""
Перепиши материал в виде поста для Telegram.

Требования:
- 120–220 слов
- 1 заголовок (первая строка)
- 3–6 буллетов или коротких абзацев
- В конце: 1 вопрос аудитории
- Не выдумывай факты, опирайся только на текст ниже
- Без ссылок, без хэштегов

Источник: {item.source}
Title: {item.title}
Summary: {item.summary}

RAW:
{raw}
""".strip()

def generate_post_for_item(item: NewItem) -> str:
    prompt = build_prompt(item)
    return generate_text(prompt)
