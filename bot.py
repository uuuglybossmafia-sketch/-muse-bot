import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

MENU, CHORDS, MIXING, MASTERING, CHAT = range(5)

MAIN_KEYBOARD = ReplyKeyboardMarkup([
    [KeyboardButton("🎸 Аккорды"), KeyboardButton("🎚️ Сведение")],
    [KeyboardButton("🔊 Мастеринг"), KeyboardButton("💬 Свободный чат")],
    [KeyboardButton("🏠 Главное меню")]
], resize_keyboard=True)

SYSTEM_PROMPTS = {
    CHORDS: "Ты профессиональный музыкальный теоретик и продюсер. Помогаешь с подбором и анализом аккордов, прогрессий, тональностей. Давай конкретные советы с примерами из известной музыки. Отвечай по-русски.",
    MIXING: "Ты опытный звукорежиссёр и mixing engineer. Давай конкретные советы по сведению: EQ, компрессия, реверб, панорама. Называй реальные плагины (Fabfilter, Waves, iZotope), конкретные значения в Hz и dB. Отвечай по-русски.",
    MASTERING: "Ты профессиональный mastering engineer. Помогаешь с финальной обработкой треков: LUFS, лимитинг, тональный баланс. Знаешь стандарты всех платформ. Отвечай по-русски.",
    CHAT: "Ты MUSE — AI-ассистент по музыкальному продакшну. Помогаешь с теорией музыки, аранжировкой, выбором инструментов. Отвечай дружелюбно по-русски."
}

MODE_NAMES = {
    CHORDS: "🎸 Режим: Аккорды",
    MIXING: "🎚️ Режим: Сведение",
    MASTERING: "🔊 Режим: Мастеринг",
    CHAT: "💬 Свободный чат"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "👋 Привет! Я *MUSE* — твой AI-ассистент по музыкальному продакшну.\n\n"
        "🎸 *Аккорды* — подбор прогрессий\n"
        "🎚️ *Сведение* — EQ, компрессия, баланс\n"
        "🔊 *Мастеринг* — LUFS, лимитинг, форматы\n"
        "💬 *Чат* — любые вопросы о музыке\n\n"
        "Выбери раздел 👇",
        parse_mode="Markdown",
        reply_markup=MAIN_KEYBOARD
    )
    return MENU

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    modes = {
        "🎸 Аккорды": (CHORDS, "🎸 *Режим: Аккорды*\n\nНапример: «Подбери прогрессию в Am для хип-хопа»\n\nНапиши свой вопрос 👇"),
        "🎚️ Сведение": (MIXING, "🎚️ *Режим: Сведение*\n\nНапример: «Бас и кик конфликтуют — как разделить?»\n\nНапиши свой вопрос 👇"),
        "🔊 Мастеринг": (MASTERING, "🔊 *Режим: Мастеринг*\n\nНапример: «Какой LUFS нужен для Spotify?»\n\nНапиши свой вопрос 👇"),
        "💬 Свободный чат": (CHAT, "💬 *Свободный чат*\n\nЗадавай любые вопросы о музыке!\n\nНапиши свой вопрос 👇"),
    }
    if text in modes:
        mode, msg = modes[text]
        context.user_data['mode'] = mode
        context.user_data['history'] = []
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=MAIN_KEYBOARD)
        return mode
    elif text == "🏠 Главное меню":
        return await start(update, context)
    return MENU

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🏠 Главное меню":
        return await start(update, context)
    if text in ["🎸 Аккорды", "🎚️ Сведение", "🔊 Мастеринг", "💬 Свободный чат"]:
        return await handle_menu(update, context)

    mode = context.user_data.get('mode', CHAT)
    history = context.user_data.get('history', [])
    await update.message.chat.send_action("typing")
    history.append({"role": "user", "content": text})
    if len(history) > 10:
        history = history[-10:]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": SYSTEM_PROMPTS[mode]}] + history,
            max_tokens=800
        )
        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        context.user_data['history'] = history
        await update.message.reply_text(
            f"{MODE_NAMES.get(mode, '')}\n\n{reply}",
            reply_markup=MAIN_KEYBOARD
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("⚠️ Ошибка. Попробуй ещё раз.", reply_markup=MAIN_KEYBOARD)
    return mode

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu)],
            CHORDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
            MIXING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
            MASTERING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
            CHAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    app.add_handler(conv)
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
