import os
import time
import requests
import json

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

TG = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
OAI = "https://api.openai.com/v1/chat/completions"

user_data = {}

SYSTEM_PROMPTS = {
    "chords": "Ты профессиональный музыкальный теоретик и продюсер. Помогаешь с подбором и анализом аккордов, прогрессий, тональностей. Давай конкретные советы с примерами из известной музыки. Отвечай по-русски.",
    "mixing": "Ты опытный звукорежиссёр и mixing engineer. Давай конкретные советы по сведению: EQ, компрессия, реверб, панорама. Называй реальные плагины (Fabfilter, Waves, iZotope), конкретные значения в Hz и dB. Отвечай по-русски.",
    "mastering": "Ты профессиональный mastering engineer. Помогаешь с финальной обработкой треков: LUFS, лимитинг, тональный баланс. Знаешь стандарты всех платформ. Отвечай по-русски.",
    "chat": "Ты MUSE — AI-ассистент по музыкальному продакшну. Помогаешь с теорией музыки, аранжировкой, выбором инструментов. Отвечай дружелюбно по-русски."
}

MODE_NAMES = {
    "chords": "🎸 Аккорды",
    "mixing": "🎚️ Сведение",
    "mastering": "🔊 Мастеринг",
    "chat": "💬 Чат"
}

MAIN_KEYBOARD = [
    ["🎸 Аккорды", "🎚️ Сведение"],
    ["🔊 Мастеринг", "💬 Свободный чат"]
]

def ask_openai(system, history):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "system", "content": system}] + history,
        "max_tokens": 800
    }
    r = requests.post(OAI, headers=headers, json=data, timeout=30)
    def ask_openai(system, history):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "system", "content": system}] + history,
        "max_tokens": 800
    }

    r = requests.post(OAI, headers=headers, json=data, timeout=30)

    print(r.status_code)
    print(r.text)

    response = r.json()

    if "choices" not in response:
        error_msg = response.get("error", {}).get("message", "Unknown error")
        raise Exception(error_msg)

    return response["choices"][0]["message"]["content"]

def send_message(chat_id, text, keyboard=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if keyboard:
        payload["reply_markup"] = {"keyboard": keyboard, "resize_keyboard": True}
    requests.post(f"{TG}/sendMessage", json=payload)

def send_typing(chat_id):
    requests.post(f"{TG}/sendChatAction", json={"chat_id": chat_id, "action": "typing"})

def handle_start(chat_id):
    user_data[chat_id] = {"mode": "chat", "history": []}
    send_message(chat_id,
        "👋 Привет! Я *MUSE* — твой AI-ассистент по музыкальному продакшну.\n\n"
        "🎸 *Аккорды* — подбор прогрессий\n"
        "🎚️ *Сведение* — EQ, компрессия, баланс\n"
        "🔊 *Мастеринг* — LUFS, лимитинг, форматы\n"
        "💬 *Чат* — любые вопросы о музыке\n\n"
        "Выбери раздел 👇",
        MAIN_KEYBOARD
    )

def handle_text(chat_id, text):
    if chat_id not in user_data:
        user_data[chat_id] = {"mode": "chat", "history": []}

    mode_map = {
        "🎸 Аккорды": "chords",
        "🎚️ Сведение": "mixing",
        "🔊 Мастеринг": "mastering",
        "💬 Свободный чат": "chat"
    }

    if text in mode_map:
        mode = mode_map[text]
        user_data[chat_id]["mode"] = mode
        user_data[chat_id]["history"] = []
        hints = {
            "chords": "Например: «Подбери прогрессию в Am для хип-хопа»",
            "mixing": "Например: «Бас и кик конфликтуют — как разделить?»",
            "mastering": "Например: «Какой LUFS нужен для Spotify?»",
            "chat": "Задавай любые вопросы о музыке!"
        }
        send_message(chat_id, f"*{MODE_NAMES[mode]}*\n\n{hints[mode]}\n\nНапиши свой вопрос 👇", MAIN_KEYBOARD)
        return

    mode = user_data[chat_id].get("mode", "chat")
    history = user_data[chat_id].get("history", [])

    send_typing(chat_id)
    history.append({"role": "user", "content": text})
    if len(history) > 10:
        history = history[-10:]

    try:
        reply = ask_openai(SYSTEM_PROMPTS[mode], history)
        history.append({"role": "assistant", "content": reply})
        user_data[chat_id]["history"] = history
        send_message(chat_id, f"*{MODE_NAMES[mode]}*\n\n{reply}", MAIN_KEYBOARD)
    except Exception as e:
        send_message(chat_id, f"⚠️ Ошибка: {str(e)}", MAIN_KEYBOARD)

def main():
    print("MUSE Bot started!")
    offset = 0
    while True:
        try:
            r = requests.get(f"{TG}/getUpdates", params={"offset": offset, "timeout": 30}, timeout=35)
            updates = r.json().get("result", [])
            for update in updates:
                offset = update["update_id"] + 1
                msg = update.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                text = msg.get("text", "")
                if not chat_id or not text:
                    continue
                if text == "/start":
                    handle_start(chat_id)
                else:
                    handle_text(chat_id, text)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
