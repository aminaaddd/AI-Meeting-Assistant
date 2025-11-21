import sounddevice as sd
import soundfile as sf
import numpy as np
from faster_whisper import WhisperModel
from typing import Optional

_MODEL: Optional[WhisperModel] = None


def get_model():
    """Load and cache the Whisper model (base version)."""
    global _MODEL
    if _MODEL is None:
        _MODEL = WhisperModel("base", compute_type="auto")
    return _MODEL


def pick_input_device(preferred_index: int | None = None) -> int:
    """Pick the input microphone device automatically or by index."""
    devices = sd.query_devices()
    if preferred_index is not None:
        return preferred_index

    # auto-pick: first device with at least 1 input channel
    for i, d in enumerate(devices):
        if d.get("max_input_channels", 0) > 0:
            return i

    raise RuntimeError(
        "No input device available. Plug in a microphone and check Windows permissions."
    )


def record_to_wav(path: str, seconds: int = 10, fs: int | None = None, device_index: int | None = None):
    """Record audio from the microphone and save to a WAV file."""
    dev = pick_input_device(device_index)
    dev_info = sd.query_devices(dev)

    # Use the device’s default sample rate if available, otherwise 16000 Hz
    samplerate = int(fs or dev_info.get("default_samplerate", 16000))

    print(f"🎙️ Recording {seconds}s on device #{dev} ({dev_info['name']}) @ {samplerate} Hz...")
    sd.default.device = (dev, None)  # (input, output)
    sd.default.samplerate = samplerate

    audio = sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=1, dtype="float32")
    sd.wait()
    audio = np.squeeze(audio)
    sf.write(path, audio, samplerate)
    print(f"✅ Saved to {path}")


def transcribe_file(path: str, language: str = None, vad_filter: bool = False) -> str:
    """
    Transcribe an audio file.

    vad_filter: when True, applies voice-activity detection filtering,
    which removes short or low-energy segments. Set to False to keep
    more words (safer if you notice missing text).
    """
    model = get_model()
    segments, info = model.transcribe(path, language=language, vad_filter=vad_filter)
    text = " ".join(seg.text.strip() for seg in segments)
    return text.strip()


def transcribe_with_confidence(path: str, language: str = None, vad_filter: bool = False):
    """
    Returns:
    - text: the full concatenated transcription
    - avg_no_speech_prob: estimated probability that it was not speech
    - segments_info: raw list of segments if you want to log or analyze them
    """
    model = get_model()
    segments, info = model.transcribe(path, language=language, vad_filter=vad_filter)

    texts = []
    no_speech_scores = []
    seg_dump = []

    for seg in segments:
        seg_text = seg.text.strip()
        texts.append(seg_text)

        # Some faster-whisper versions expose these fields:
        # seg.no_speech_prob, seg.avg_logprob, seg.compression_ratio
        ns = getattr(seg, "no_speech_prob", None)
        if ns is not None:
            no_speech_scores.append(ns)

        seg_dump.append({
            "start": seg.start,
            "end": seg.end,
            "text": seg_text,
            "no_speech_prob": ns
        })

    full_text = " ".join(t for t in texts).strip()
    avg_no_speech = sum(no_speech_scores) / len(no_speech_scores) if no_speech_scores else 0.0

    return full_text, avg_no_speech, seg_dump
