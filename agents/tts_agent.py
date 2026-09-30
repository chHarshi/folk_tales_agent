import os, uuid
from gtts import gTTS
import config

class TTSAgent:
    SUPPORTED = {"en", "hi", "te"}

    def speak(self, text, language="en"):
        if not text or not text.strip():
            raise ValueError("No text provided for narration.")
        if language not in self.SUPPORTED:
            language = "en"
        audio_dir = os.path.join(config.OUTPUT_DIR, "audio")
        os.makedirs(audio_dir, exist_ok=True)
        path = os.path.join(audio_dir, f"{uuid.uuid4().hex}.mp3")
        gTTS(text=text, lang=language, slow=False).save(path)
        return path