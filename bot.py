import os
import time
import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

TG = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Ключевые слова музыкальной тематики
MUSIC_WORDS = [
    "музыка",
    "трек",
    "бит",
    "рэп",
    "хип хоп",
    "песня",
    "вокал",
    "fl studio",
    "ableton",
    "logic pro",
    "cubase",
    "studio one",
    "сведение",
    "мастеринг",
    "микс",
    "плагин",
    "аккорд",
    "мелодия",
    "аранжировка",
    "драм",
    "808",
    "бас",
    "лирика",
    "жанр",
    "артист",
    "исполнитель"
]


def is_music_related(text):
    text = text.lower()

    return any(word in text for word in MUSIC_WORDS)


def ask_ai(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = """
Ты музыкальный AI ассистент.

Ты отвечаешь ТОЛЬКО на темы:
- музыка
- артисты
- рэп
- биты
- сведение
- мастеринг
- FL Studio
- Ableton
- плагины
- аккорды
- тексты песен
- жанры
- теория музыки

Если вопрос не связан с музыкой —
отвечай:

"Я музыкальный ассистент и отвечаю только на музыкальные темы."

Отвечай кратко, понятно и по делу.
Не выдумывай факты.
"""

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2,
        "max_tokens": 250
    }

    r = requests.post(
        API_URL,
        headers=headers,
        json=data,
        timeout=60
    )

    print("STATUS:", r.status_code)
    print("RESPONSE:", r.text)

    response = r.json()

    if "choices" not in response:
        raise Exception(str(response))

    return response["choices"][0]["message"]["content"]


def send_message(chat_id, text):
    requests.post(
        f"{TG}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        }
    )


def main():
    print("BOT STARTED")

    offset = 0

    while True:
        try:
            r = requests.get(
                f"{TG}/getUpdates",
                params={
                    "offset": offset,
                    "timeout": 30
                },
                timeout=35
            )

            data = r.json()

            if "result" not in data:
                print(data)
                time.sleep(3)
                continue

            updates = data["result"]

            for update in updates:
                offset = update["update_id"] + 1

                msg = update.get("message")

                if not msg:
                    continue

                chat_id = msg["chat"]["id"]
                text = msg.get("text")

                if not text:
                    continue

                print(f"USER: {text}")

                # Проверка музыкальной темы
                if not is_music_related(text):
                    send_message(
                        chat_id,
                        "Я музыкальный ассистент и отвечаю только на музыкальные темы."
                    )
                    continue

                try:
                    answer = ask_ai(text)

                    print(f"AI: {answer}")

                    send_message(chat_id, answer)

                except Exception as e:
                    print("AI ERROR:", e)

                    send_message(
                        chat_id,
                        f"Ошибка AI:\n{str(e)}"
                    )

        except Exception as e:
            print("MAIN ERROR:", e)
            time.sleep(5)


if __name__ == "__main__":
    main()
