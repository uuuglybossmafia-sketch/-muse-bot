import os
import time
import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

TG = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

API_URL = "https://api.groq.com/openai/v1/chat/completions"


def ask_ai(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": "Ты полезный AI ассистент. Отвечай по-русски."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    r = requests.post(
        API_URL,
        headers=headers,
        json=data,
        timeout=60
    )

    print(r.status_code)
    print(r.text)

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

            updates = r.json()["result"]

            for update in updates:
                offset = update["update_id"] + 1

                msg = update.get("message")

                if not msg:
                    continue

                chat_id = msg["chat"]["id"]
                text = msg.get("text")

                if not text:
                    continue

                try:
                    answer = ask_ai(text)
                    send_message(chat_id, answer)

                except Exception as e:
                    send_message(chat_id, f"Ошибка:\n{str(e)}")

        except Exception as e:
            print(e)
            time.sleep(5)


if __name__ == "__main__":
    main()
