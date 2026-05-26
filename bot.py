import os
import time
import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

TG_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

AI_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """
Ты музыкальный AI ассистент.

Помогай:
- с аккордами
- мелодиями
- басом
- драм партиями
- ритмами
- грувом
- жанрами
- теорией музыки

Отвечай только на музыкальные темы.
"""

def send_message(chat_id, text):

    requests.post(
        f"{TG_API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        }
    )

def ask_ai(user_text):

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
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
        "temperature": 0.3,
        "max_tokens": 300
    }

    response = requests.post(
        AI_URL,
        headers=headers,
        json=data
    )

    result = response.json()

    return result["choices"][0]["message"]["content"]

def main():

    offset = 0

    while True:

        try:

            response = requests.get(
                f"{TG_API}/getUpdates",
                params={
                    "offset": offset,
                    "timeout": 30
                }
            )

            updates = response.json()["result"]

            for update in updates:

                offset = update["update_id"] + 1

                message = update.get("message")

                if not message:
                    continue

                text = message.get("text")

                if not text:
                    continue

                chat_id = message["chat"]["id"]

                answer = ask_ai(text)

                send_message(chat_id, answer)

        except Exception as e:

            print(e)

            time.sleep(5)

if __name__ == "__main__":
    main()
