from agents.rag_agent import RAGAgent
from agents.tts_agent import TTSAgent
from agents.image_agent import ImageAgent

class CoordinatorAgent:
    def __init__(self):
        self.rag = RAGAgent()
        self.tts = TTSAgent()
        self.image_agent = ImageAgent()

    def handle_query(self, query, language="en", do_tts=True, do_image=False):
        story, context = self.rag.run(query)

        audio_path = None
        image_path = None

        if do_tts:
            audio_path = self.tts.speak(
                text=story,
                language=language,
                save_file="output_audio.mp3"
            )

        if do_image:
            image_path = self.image_agent.generate_image(story)

        return {
            "story": story,
            "audio": audio_path,
            "image": image_path
        }

