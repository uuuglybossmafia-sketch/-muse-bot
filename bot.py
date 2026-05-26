import os
import time
import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY")

TG = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

API_URL = "https://api.together.xyz/v1/chat/completions"

def ask_ai(prompt):
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }

    r = requests.post(API_URL, headers=headers, json=data)

    print(r.status_code)
    print(r.text)

    response = r.json()

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
    offset = 0

    while True:
        try:
            r = requests.get(
                f"{TG}/getUpdates",
                params={
                    "offset": offset,
                    "timeout": 30
                }
            )

            updates = r.json()["result"]

            for update in updates:
                offset = update["update_id"] + 1

                msg = update.get("message")

                if not msg:
                    continue

                chat_id = msg["chat"]["id"]
                text = msg.get("text", "")

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
