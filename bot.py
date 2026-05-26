for update in updates:

    offset = update["update_id"] + 1

    message = update.get("message")

    if not message:
        continue

    chat_id = message["chat"]["id"]

    # =========================
    # AUDIO FILE
    # =========================

    if "audio" in message:

        try:

            send_message(chat_id, "Скачиваю аудио...")

            file_id = message["audio"]["file_id"]

            filename = download_file(file_id)

            send_message(chat_id, "Анализирую BPM и тональность...")

            features = analyze_audio_features(filename)

            send_message(
                chat_id,
                f"""
🎵 BPM: {features['bpm']}
🎹 KEY: {features['key']}
🔊 BRIGHTNESS: {features['brightness']}
📢 LOUDNESS: {features['loudness']}
"""
            )

            send_message(chat_id, "Распознаю вокал...")

            transcription = transcribe_audio(filename)

            send_message(chat_id, "AI анализирует трек...")

            analysis = analyze_track(
                transcription,
                features
            )

            send_message(chat_id, analysis)

        except Exception as e:

            print("AUDIO ERROR:", e)

            send_message(
                chat_id,
                f"Ошибка анализа аудио:\n{str(e)}"
            )

        continue

    # =========================
    # VOICE MESSAGE
    # =========================

    if "voice" in message:

        try:

            send_message(chat_id, "Обрабатываю голосовое...")

            file_id = message["voice"]["file_id"]

            filename = download_file(file_id)

            features = analyze_audio_features(filename)

            transcription = transcribe_audio(filename)

            analysis = analyze_track(
                transcription,
                features
            )

            send_message(chat_id, analysis)

        except Exception as e:

            print("VOICE ERROR:", e)

            send_message(
                chat_id,
                f"Ошибка обработки голосового:\n{str(e)}"
            )

        continue

    # =========================
    # TEXT MESSAGE
    # =========================

    text = message.get("text")

    if not text:
        continue

    try:

        answer = ask_ai(text)

        send_message(chat_id, answer)

    except Exception as e:

        print("TEXT ERROR:", e)

        send_message(
            chat_id,
            f"Ошибка AI:\n{str(e)}"
        )
