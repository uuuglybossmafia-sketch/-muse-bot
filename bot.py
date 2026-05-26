import os
import time
import requests

# ENV
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY")

# URL
TG = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
API_URL = "https://api.together.xyz/v1/chat/completions"


# AI
def ask_ai(prompt):
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
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
        "max_tokens": 500,
        "temperature": 0.7
    }

    r = requests.post(
        API_URL,
        headers=headers,
        json=data,
        timeout=60
    )

    print("STATUS:", r.status_code)
    print("TEXT:", r.text)

    response = r.json()

    # ПРОВЕРКА ОШИБКИ
    if "choices" not in response:
        error_message = response.get("error", {}).get(
            "message",
            str(response)
        )

        raise Exception(error_message)

    return response["choices"][0]["message"]["content"]


# TELEGRAM
def send_message(chat_id, text):
    requests.post(
        f"{TG}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        }
    )


# MESSAGE HANDLER
def handle_message(chat_id, text):
    try:
        answer = ask_ai(text)
        send_message(chat_id, answer)

    except Exception as e:
        print("ERROR:", str(e))

        send_message(
            chat_id,
            f"Ошибка:\n{str(e)}"
        )


# MAIN LOOP
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

                message = update.get("message")

                if not message:
                    continue

                chat_id = message["chat"]["id"]
                text = message.get("text")

                if not text:
                    continue

                handle_message(chat_id, text)

        except Exception as e:
            print("MAIN ERROR:", str(e))
            time.sleep(5)


if __name__ == "__main__":
    main()
