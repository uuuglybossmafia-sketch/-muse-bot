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

# States
MENU, CHORDS, MIXING, MASTERING, CHAT = range(5)

MAIN_KEYBOARD = ReplyKeyboardMarkup([
    [KeyboardButton("🎸 Аккорды"), KeyboardButton("🎚️ Сведение")],
    [KeyboardButton("🔊 Мастеринг"), KeyboardButton("💬 Свободный чат")],
    [KeyboardButton("🏠 Главное меню")]
], resize_keyboard=True)

SYSTEM_PROMPTS = {
    CHORDS: """Ты профессиональный музыкальный теоретик и продюсер. 
Помогаешь с подбором и анализом аккордов, прогрессий, тональностей. 
Давай конкретные советы с примерами из известной музыки. 
Предлагай варианты развития прогрессии. Отвечай по-русски.""",

    MIXING: """Ты опытный звукорежиссёр и mixing engineer. 
Давай конкретные советы по сведению: EQ, компрессия, реверб, панорама, частоты.
Называй реальные плагины (Fabfilter, Waves, iZotope), конкретные значения в Hz и dB.
Отвечай по-русски.""",

    MASTERING: """Ты профессиональный mastering engineer.
Помогаешь с финальной обработкой треков: LUFS, лимитинг, тональный баланс, форматы.
Знаешь стандарты всех платформ (Spotify -14 LUFS, YouTube -14 LUFS, CD -9 LUFS и т.д.).
Давай чёткий чеклист и конкретные рекомендации. Отвечай по-русски.""",

    CHAT: """Ты MUSE — AI-ассистент по музыкальному продакшну.
Помогаешь с теорией музыки, аранжировкой, выбором инструментов, советами по карьере.
Отвечай дружелюбно и профессионально по-русски."""
}

MODE_NAMES = {
    CHORDS: "🎸 Режим: Аккорды",
    MIXING: "🎚️ Режим: Сведение",
    MASTERING: "🔊 Режим: Мастеринг",
    CHAT: "💬 Режим: Свободный чат"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "👋 Привет! Я *MUSE* — твой AI-ассистент по музыкальному продакшну.\n\n"
        "Могу помочь с:\n"
        "🎸 *Аккорды* — подбор прогрессий, анализ тональностей\n"
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

    if text == "🎸 Аккорды":
        context.user_data['mode'] = CHORDS
        context.user_data['history'] = []
        await update.message.reply_text(
            "🎸 *Режим: Аккорды*\n\n"
            "Спроси что угодно! Например:\n"
            "• «Подбери прогрессию в Am для хип-хопа»\n"
            "• «Какие аккорды заменить в C - Am - F - G?»\n"
            "• «Объясни функцию dim аккорда»\n\n"
            "Напиши свой вопрос 👇",
            parse_mode="Markdown",
            reply_markup=MAIN_KEYBOARD
        )
        return CHORDS

    elif text == "🎚️ Сведение":
        context.user_data['mode'] = MIXING
        context.user_data['history'] = []
        await update.message.reply_text(
            "🎚️ *Режим: Сведение*\n\n"
            "Спроси что угодно! Например:\n"
            "• «Бас и кик конфликтуют — как разделить?»\n"
            "• «Вокал теряется в миксе»\n"
            "• «Какой EQ поставить на барабаны в трэпе?»\n\n"
            "Напиши свой вопрос 👇",
            parse_mode="Markdown",
            reply_markup=MAIN_KEYBOARD
        )
        return MIXING

    elif text == "🔊 Мастеринг":
        context.user_data['mode'] = MASTERING
        context.user_data['history'] = []
        await update.message.reply_text(
            "🔊 *Режим: Мастеринг*\n\n"
            "Спроси что угодно! Например:\n"
            "• «Какой LUFS нужен для Spotify?»\n"
            "• «Трек звучит тихо — что делать?»\n"
            "• «Чеклист перед сдачей на дистрибуцию»\n\n"
            "Напиши свой вопрос 👇",
            parse_mode="Markdown",
            reply_markup=MAIN_KEYBOARD
        )
        return MASTERING

    elif text == "💬 Свободный чат":
        context.user_data['mode'] = CHAT
        context.user_data['history'] = []
        await update.message.reply_text(
            "💬 *Свободный чат*\n\n"
            "Задавай любые вопросы о музыке, продакшне, теории, карьере — всё что угодно!\n\n"
            "Напиши свой вопрос 👇",
            parse_mode="Markdown",
            reply_markup=MAIN_KEYBOARD
        )
        return CHAT

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

    # Show typing
    await update.message.chat.send_action("typing")

    history.append({"role": "user", "content": text})

    # Keep history max 10 messages
    if len(history) > 10:
        history = history[-10:]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS[mode]}
            ] + history,
            max_tokens=800,
            temperature=0.7
        )

        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        context.user_data['history'] = history

        mode_label = MODE_NAMES.get(mode, "")
        await update.message.reply_text(
            f"{mode_label}\n\n{reply}",
            reply_markup=MAIN_KEYBOARD
        )

    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        await update.message.reply_text(
            "⚠️ Ошибка при обращении к AI. Попробуй ещё раз.",
            reply_markup=MAIN_KEYBOARD
        )

    return mode

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
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

    app.add_handler(conv_handler)

    logger.info("MUSE Bot started!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
