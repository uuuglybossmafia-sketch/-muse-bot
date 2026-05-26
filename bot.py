# =========================================================
# ADD THESE IMPORTS
# =========================================================

import librosa
import numpy as np

# =========================================================
# AUDIO FEATURE ANALYSIS
# =========================================================

def analyze_audio_features(filename):

    y, sr = librosa.load(filename)

    # BPM
    tempo, _ = librosa.beat.beat_track(
        y=y,
        sr=sr
    )

    bpm = round(float(tempo))

    # KEY DETECTION
    chroma = librosa.feature.chroma_stft(
        y=y,
        sr=sr
    )

    chroma_mean = chroma.mean(axis=1)

    notes = [
        "C", "C#", "D", "D#",
        "E", "F", "F#", "G",
        "G#", "A", "A#", "B"
    ]

    key = notes[np.argmax(chroma_mean)]

    # SPECTRAL BRIGHTNESS
    spectral_centroid = librosa.feature.spectral_centroid(
        y=y,
        sr=sr
    )

    brightness = round(float(np.mean(spectral_centroid)))

    # NOISINESS
    zcr = librosa.feature.zero_crossing_rate(y)

    noisiness = round(float(np.mean(zcr) * 1000), 2)

    # LOUDNESS
    rms = librosa.feature.rms(y=y)

    loudness = round(float(np.mean(rms) * 100), 2)

    return {
        "bpm": bpm,
        "key": key,
        "brightness": brightness,
        "noisiness": noisiness,
        "loudness": loudness
    }

# =========================================================
# DOWNLOAD TELEGRAM FILE
# =========================================================

def download_file(file_id):

    r = requests.get(
        f"{TG_API}/getFile",
        params={
            "file_id": file_id
        }
    )

    data = r.json()

    file_path = data["result"]["file_path"]

    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"

    filename = file_path.split("/")[-1]

    file_data = requests.get(file_url)

    with open(filename, "wb") as f:
        f.write(file_data.content)

    return filename

# =========================================================
# WHISPER TRANSCRIPTION
# =========================================================

def transcribe_audio(filename):

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    files = {
        "file": open(filename, "rb")
    }

    data = {
        "model": "whisper-large-v3"
    }

    r = requests.post(
        "https://api.groq.com/openai/v1/audio/transcriptions",
        headers=headers,
        files=files,
        data=data
    )

    response = r.json()

    print(response)

    if "text" not in response:
        return "Не удалось распознать аудио."

    return response["text"]

# =========================================================
# AI TRACK ANALYSIS
# =========================================================

def analyze_track(transcription, features):

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
Проанализируй музыкальный трек.

Характеристики трека:

BPM: {features['bpm']}
KEY: {features['key']}
BRIGHTNESS: {features['brightness']}
NOISINESS: {features['noisiness']}
LOUDNESS: {features['loudness']}

Текст трека:
{transcription}

Сделай:
1. Определение жанра
2. Анализ сведения
3. Анализ мастеринга
4. Анализ вокала
5. Коммерческая оценка
6. Что улучшить
7. Сильные стороны

Отвечай как музыкальный продюсер.
"""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 700
    }

    r = requests.post(
        CHAT_URL,
        headers=headers,
        json=payload
    )

    response = r.json()

    print(response)

    return response["choices"][0]["message"]["content"]

# =========================================================
# ADD THIS INSIDE YOUR MAIN LOOP
# AFTER:
# message = update.get("message")
# =========================================================

# =========================
# AUDIO
# =========================

if "audio" in message:

    chat_id = message["chat"]["id"]

    send_message(chat_id, "Скачиваю аудио...")

    file_id = message["audio"]["file_id"]

    filename = download_file(file_id)

    send_message(chat_id, "Анализирую BPM и тональность...")

    features = analyze_audio_features(filename)

    send_message(
        chat_id,
        f"""
BPM: {features['bpm']}
KEY: {features['key']}
BRIGHTNESS: {features['brightness']}
LOUDNESS: {features['loudness']}
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

    continue

# =========================
# VOICE
# =========================

if "voice" in message:

    chat_id = message["chat"]["id"]

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

    continue
