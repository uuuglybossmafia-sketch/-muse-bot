import os
import time
import requests

# =========================
# ENV
# =========================

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not TELEGRAM_TOKEN:
    raise Exception("Нет TELEGRAM_TOKEN")

if not GROQ_API_KEY:
    raise Exception("Нет GROQ_API_KEY")

# =========================
# URLS
# =========================

TG_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# =========================
# AI
# =========================

SYSTEM_PROMPT = """
Ты профессиональный музыкальный AI ассистент.

Ты специализируешься ТОЛЬКО на:
- музыке
- рэпе
- битах
- вокале
- сведении
- мастеринге
- FL Studio
- Ableton
- Logic Pro
- плагинах
- написании песен
- теории музыки
- жанрах
- артистах
- записи звука
- обработке вокала

Если вопрос не связан с музыкой —
отвечай только:

"Я музыкальный ассистент и отвечаю только на музыкальные темы."

Если вопрос хотя бы частично связан с музыкой —
обязательно помогай.

Отвечай:
- кратко
- понятно
- по делу

Не придумывай факты.
"""

# =========================
# SEND MESSAGE
# =========================

def send_message(chat_id, text):
    try:
        requests.post(
            f"{TG_API}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text
            },
            timeout=20
        )

    except Exception as e:
        print("SEND MESSAGE ERROR:", e)

# =========================
# ASK AI
# =========================

def ask_ai(user_text):

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_text
            }
        ],
        "temperature": 0.2,
        "max_tokens": 250
    }

    response = requests.post(
        GROQ_API_URL,
        headers=headers,
        json=payload,
        timeout=60
    )

    print("AI STATUS:", response.status_code)
    print("AI RESPONSE:", response.text)

    data = response.json()

    if "choices" not in data:
        raise Exception(str(data))

    answer = data["choices"][0]["message"]["content"]

    if not answer:
        return "Ошибка генерации ответа."

    return answer.strip()

# =========================
# GET UPDATES
# =========================

def get_updates(offset):

    response = requests.get(
        f"{TG_API}/getUpdates",
        params={
            "offset": offset,
            "timeout": 30
        },
        timeout=35
    )

    data = response.json()

    if "result" not in data:
        return []

    return data["result"]

# =========================
# MAIN
# =========================

def main():

    print("BOT STARTED")

    offset = 0

    while True:

        try:

            updates = get_updates(offset)

            for update in updates:

                offset = update["update_id"] + 1

                message = update.get("message")

                if not message:
                    continue

                chat_id = message["chat"]["id"]

                text = message.get("text")

                if not text:
                    continue

                print(f"\nUSER: {text}")

                try:

                    answer = ask_ai(text)

                    print(f"AI: {answer}")

                    send_message(chat_id, answer)

                except Exception as ai_error:

                    print("AI ERROR:", ai_error)

                    send_message(
                        chat_id,
                        f"Ошибка AI:\n{str(ai_error)}"
                    )

        except Exception as main_error:

            print("MAIN ERROR:", main_error)

            time.sleep(5)

# =========================
# START
# =========================

if __name__ == "__main__":
    main()
