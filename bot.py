# =========================
# AUDIO
# =========================

if "audio" in message:

    chat_id = message["chat"]["id"]

    try:

        send_message(chat_id, "Скачиваю аудио...")

        file_id = message["audio"]["file_id"]

        filename = download_file(file_id)

        send_message(chat_id, "Распознаю аудио...")

        transcription = transcribe_audio(filename)

        send_message(chat_id, "AI анализирует трек...")

        analysis = analyze_track(transcription)

        send_message(chat_id, analysis)

    except Exception as e:

        print(e)

        send_message(
            chat_id,
            f"Ошибка анализа:\n{str(e)}"
        )

    continue

# =========================
# VOICE
# =========================

if "voice" in message:

    chat_id = message["chat"]["id"]

    try:

        send_message(chat_id, "Обрабатываю голосовое...")

        file_id = message["voice"]["file_id"]

        filename = download_file(file_id)

        transcription = transcribe_audio(filename)

        analysis = analyze_track(transcription)

        send_message(chat_id, analysis)

    except Exception as e:

        print(e)

        send_message(
            chat_id,
            f"Ошибка voice:\n{str(e)}"
        )

    continue
