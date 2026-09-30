import os, uuid, time, logging
from huggingface_hub import InferenceClient
from utils.llm import get_llm
import config

log = logging.getLogger(__name__)

SCENE_PROMPT = """Read this Indian folk tale and write ONE image-generation prompt (max 60 words)
describing its most memorable scene. Style: warm traditional Indian storybook illustration,
vibrant colors, no text or lettering in the image. Output only the prompt, nothing else.

Tale:
{story}"""

class ImageAgent:
    def __init__(self):
        token = os.getenv("HF_TOKEN")
        self.client = InferenceClient(api_key=token) if token else None
        self.llm = get_llm(config.IMAGE_SCENE_LLM_PROVIDER, temperature=0.5)

    def generate_image(self, story):
        if self.client is None:
            log.warning("HF_TOKEN not set; skipping image generation.")
            return None
        try:
            prompt = self.llm.invoke(SCENE_PROMPT.format(story=story[:3000])).content.strip()
        except Exception as e:
            log.warning("Scene prompt generation failed: %s", e)
            return None

        image_dir = os.path.join(config.OUTPUT_DIR, "images")
        os.makedirs(image_dir, exist_ok=True)
        path = os.path.join(image_dir, f"{uuid.uuid4().hex}.png")

        for attempt in range(3):
            try:
                image = self.client.text_to_image(prompt, model=config.HF_IMAGE_MODEL)
                image.save(path)
                return path
            except Exception as e:
                msg = str(e)
                if "loading" in msg.lower() or "503" in msg:
                    wait = 20 * (attempt + 1)
                    log.info("Model loading on HF, waiting %ss (attempt %s/3)", wait, attempt + 1)
                    time.sleep(wait)
                    continue
                log.warning("Image generation failed: %s", e)
                return None
        log.warning("Image generation gave up after retries.")
        return None