from gtts import gTTS
from deep_translator import GoogleTranslator
import os
import textwrap

class TTSAgent:
    def __init__(self):
        self.lang_map = {
            "en": "en",
            "hi": "hi",
            "te": "te"
        }

    def speak(self, text, language="en", save_file="output_audio.mp3"):
        # 1. Translate ONLY if language is not English
        if language != "en":
            translator = GoogleTranslator(source="auto", target=language)

            # Split text into safe chunks (<= 4500 chars)
            chunks = textwrap.wrap(text, 4500)
            translated_chunks = []

            for chunk in chunks:
                translated_chunks.append(translator.translate(chunk))

            text = " ".join(translated_chunks)

        # 2. Generate audio
        tts = gTTS(text=text, lang=self.lang_map.get(language, "en"))
        tts.save(save_file)

        return save_file

