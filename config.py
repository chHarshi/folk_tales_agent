import os
from dotenv import load_dotenv

load_dotenv()

LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
STORY_LLM_PROVIDER = os.getenv("STORY_LLM_PROVIDER", "gemini")       # user-facing, needs quality+speed
TRANSLATE_LLM_PROVIDER = os.getenv("TRANSLATE_LLM_PROVIDER", "ollama")  # cheap, one line, fine locally
VALIDATE_LLM_PROVIDER = os.getenv("VALIDATE_LLM_PROVIDER", "ollama")    # slow either way, keep free
IMAGE_SCENE_LLM_PROVIDER = os.getenv("IMAGE_SCENE_LLM_PROVIDER", "ollama")  # short creative prompt
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gemini-2.5-flash-image")  # verify in Google's docs later
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
PERSIST_DIR = os.getenv("PERSIST_DIR", "embeddings")
STORIES_PATH = os.getenv("STORIES_PATH", "data/stories.jsonl")
COLLECTION = "folk_tales"
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "450"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
MIN_RELEVANCE = float(os.getenv("MIN_RELEVANCE", "0.40"))
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")
LANG_NAMES = {"en": "English", "hi": "Hindi", "te": "Telugu"}
HF_IMAGE_MODEL = os.getenv("HF_IMAGE_MODEL", "black-forest-labs/FLUX.1-schnell")