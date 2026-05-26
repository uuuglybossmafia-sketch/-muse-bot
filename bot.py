import os
import time
import requests

# ======================================
# TOKENS
# ======================================

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

TG_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

AI_URL = "https://api.groq.com/openai/v1/chat/completions"

# ======================================
# SYSTEM PROMPT
# ======================================

SYSTEM_PROMPT = """
Ты музыкальный AI ассистент.

Ты помогаешь:
- писать мелодии
- подбирать аккорды
- делать бас партии
- придумывать драм партии
- создавать ритмы и грув
- объяснять теорию музыки
- помогать с FL Studio и Ableton
- придумывать идеи для треков
- помогать с жанрами

Правила:
1. Отвечай кратко.
2. Отвечай понятно.
3. Не уходи в темы вне музыки.
4. Если просят аккорды — пиши их нотами.
5. Если просят драмку — пиши ритм текстом.
6. Если просят мелодию — давай простые музыкальные идеи.
"""

# ======================================
# SEND MESSAGE
# ======================================

def send_message(chat_id, text):

    requests.post(
        f"{TG_API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        }
    )

# ======================================
# SEND PHOTO
# ======================================

def send_photo(chat_id, photo_url, caption=""):

    requests.post(
        f"{TG_API}/sendPhoto",
        json={
            "chat_id": chat_id,
            "photo": photo_url,
            "caption": caption
        }
    )

# ======================================
# ASK AI
# ======================================

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
        json=data,
        timeout=60
    )

    result = response.json()

    print(result)

    if "choices" not in result:
        raise Exception(str(result))

    return result["choices"][0]["message"]["content"]

# ======================================
# MAIN
# ======================================

def main():

    print("BOT STARTED")

    offset = 0

    while True:

        try:

            response = requests.get(
                f"{TG_API}/getUpdates",
                params={
                    "offset": offset,
                    "timeout": 30
                },
                timeout=35
            )

            data = response.json()

            updates = data.get("result", [])

            for update in updates:

                offset = update["update_id"] + 1

                message = update.get("message")

                if not message:
                    continue

                text = message.get("text")

                if not text:
                    continue

                chat_id = message["chat"]["id"]

                print("USER:", text)

                try:

                    answer = ask_ai(text)

                    print("AI:", answer)

                    send_message(chat_id, answer)

                    # ======================================
                    # MUSIC PHOTOS
                    # ======================================

                    lower_text = text.lower()

                    if "trap" in lower_text:

                        send_photo(
                            chat_id,
                            "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f",
                            "Trap vibe"
                        )

                    elif "drill" in lower_text:

                        send_photo(
                            chat_id,
                            "https://images.unsplash.com/photo-1511379938547-c1f69419868d",
                            "Drill atmosphere"
                        )

                    elif "piano" in lower_text:

                        send_photo(
                            chat_id,
                            "https://images.unsplash.com/photo-1507838153414-b4b713384a76",
                            "Piano chords reference"
                        )

                    elif "guitar" in lower_text:

                        send_photo(
                            chat_id,
                            "https://images.unsplash.com/photo-1510915361894-db8b60106cb1",
                            "Guitar inspiration"
                        )

                    elif "fl studio" in lower_text:

                        send_photo(
                            chat_id,
                            "https://images.unsplash.com/photo-1516280440614-37939bbacd81",
                            "FL Studio vibe"
                        )

                    elif "ableton" in lower_text:

                        send_photo(
                            chat_id,
                            "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f",
                            "Ableton workflow"
                        )

                except Exception as e:

                    print("AI ERROR:", e)

                    send_message(
                        chat_id,
                        f"Ошибка AI:\n{str(e)}"
                    )

        except Exception as e:

            print("MAIN ERROR:", e)

            time.sleep(5)

# ======================================
# START
# ======================================

if __name__ == "__main__":
    main()
