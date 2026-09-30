from agents.rag_agent import RAGAgent
from agents.tts_agent import TTSAgent
from agents.image_agent import ImageAgent
from agents.validation_agent import ValidationAgent

class CoordinatorAgent:
    def __init__(self):
        self.rag = RAGAgent()
        self.tts = TTSAgent()
        self.image_agent = ImageAgent()
        self.validator = ValidationAgent()

    def handle_query(self, query, language="en", do_tts=True, do_image=False, do_validate=False):
        out = {"story": None, "audio": None, "image": None, "sources": [], "validation": None, "found": False}

        import time
        t0 = time.time()
        result = self.rag.run(query, language)
        print(f"[TIMING] rag.run took {time.time() - t0:.1f}s")
        out["found"] = result["found"]
        if not result["found"]:
            out["story"] = "I couldn't find a matching folk tale for that. Try mentioning a character, animal, or theme."
            return out

        story = result["story"]
        if do_validate:
            try:
                verdict = self.validator.validate(story, result["context"])
                out["validation"] = verdict
            except Exception as e:
                out["validation"] = {"error": str(e)}

        out["story"] = story
        out["sources"] = result["sources"]

        if do_tts:
            try:
                t1 = time.time()
                out["audio"] = self.tts.speak(story, language)
                print(f"[TIMING] tts.speak took {time.time() - t1:.1f}s")
            except Exception as e:
                out["audio"] = None
                print("TTS failed:", e)

        if do_image:
            out["image"] = self.image_agent.generate_image(story)

        return out