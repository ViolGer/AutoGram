import os
from functools import lru_cache

from dotenv import load_dotenv
from openai import OpenAI

# Загружаем .env один раз при импорте (это безопасно)
load_dotenv()


@lru_cache(maxsize=1)
def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY не найден. Создай .env в корне проекта и добавь строку:\n"
            "OPENAI_API_KEY=...\n"
            "Либо задай переменную окружения в системе."
        )
    return OpenAI(api_key=api_key)


def generate_text(prompt: str) -> str:
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")

    client = get_client()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Ты пишешь короткие посты для Telegram. Стиль: ясно, дружелюбно, без воды."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )
    return resp.choices[0].message.content.strip()
