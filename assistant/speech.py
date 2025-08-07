from __future__ import annotations

import json
import os
from typing import Optional

import numpy as np
import sounddevice as sd
from vosk import KaldiRecognizer, Model


SAMPLE_RATE = 16_000


def _load_model() -> Model:
    model_path = os.getenv("VOSK_MODEL_PATH")
    if not model_path or not os.path.isdir(model_path):
        raise RuntimeError(
            "VOSK_MODEL_PATH not set or invalid. Download a Vosk model (e.g., small English) "
            "and set VOSK_MODEL_PATH to the extracted folder."
        )
    return Model(model_path)


def transcribe_fixed_duration(seconds: int = 5) -> str:
    """Record microphone audio for a fixed duration and return the transcription text.
    """
    if seconds <= 0:
        seconds = 3
    model = _load_model()
    recognizer = KaldiRecognizer(model, SAMPLE_RATE)

    recording = sd.rec(
        int(seconds * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16"
    )
    sd.wait()

    # Ensure contiguous int16 bytes
    audio_bytes = np.asarray(recording, dtype=np.int16).tobytes()
    recognizer.AcceptWaveform(audio_bytes)
    result_json = recognizer.FinalResult()
    try:
        result = json.loads(result_json)
        return (result.get("text") or "").strip()
    except Exception:
        return ""


