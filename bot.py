import os
import time
import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

TG = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
OAI = "https://api.openai.com/v1/chat/completions"

user_data = {}

SYSTEM_PROMPTS = {
    "chat": "Ты полезный AI помощник. Отвечай по-русски."
}

MAIN_KEYBOARD = [
    ["💬 Чат"]
]

def ask_openai(system, history):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "system", "content": system}] + history,
        "max_tokens": 500
    }

    r = requests.post(OAI, headers=headers, json=data, timeout=30)

    print("STATUS:", r.status_code)
    print("TEXT:", r.text)

    response = r.json()

    if "choices" not in response:
        error_msg = response.get("error", {}).get("message", "OpenAI API error")
        raise Exception(error_msg)

    return response["choices"][0]["message"]["content"]

def send_message(chat_id, text):
    requests.post(
        f"{TG}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        }
    )

def handle_text(chat_id, text):
    history = [
        {
            "role": "user",
            "content": text
        }
    ]

    try:
        answer = ask_openai(
            SYSTEM_PROMPTS["chat"],
            history
        )

        send_message(chat_id, answer)

    except Exception as e:
        send_message(chat_id, f"Ошибка:\n{str(e)}")

def main():
    print("Bot started")

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
                text = message.get("text", "")

                if text:
                    handle_text(chat_id, text)

        except Exception as e:
            print("MAIN ERROR:", e)
            time.sleep(5)

if __name__ == "__main__":
    main()
