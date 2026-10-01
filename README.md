# Indian Folk Tales Agent

A multi-agent RAG (Retrieval-Augmented Generation) application that retrieves real Indian folk tales from a curated public-domain dataset and narrates them in English, Hindi, or Telugu, with optional audio narration and AI-generated illustrations.

## What this project does

1. **Retrieves** a real folk tale that matches a user's query (e.g. "a wicked magician whose life is hidden in a parrot") from a dataset of 213 tales.
2. **Narrates** the tale in the requested language, staying faithful to the original plot, using an LLM.
3. **Speaks** the story aloud via text-to-speech.
4. **Illustrates** the story's key scene with an AI-generated image (optional).
5. **Validates** the retelling's faithfulness against the source tale (available as a dev/QA tool).

## Dataset

213 real folk tales compiled from 8 public-domain collections on Project Gutenberg, covering North India, Bengal, Punjab, the Deccan, South India, and pan-Indian Jataka tales:

| Source | Region | Stories |
|---|---|---|
| Indian Fairy Tales (Jacobs, 1892) | North India | 29 |
| Folk-Tales of Bengal (Day, 1883) | East India | 22 |
| Tales of the Punjab (Steel, 1894) | Punjab | 43 |
| Old Deccan Days (Frere, 1870) | South/Central India | 24 |
| Tales of the Sun (Kingscote & Sastri, 1890) | South India | 26 |
| Jataka Tales (Babbitt, 1912) | Pan-India | 18 |
| More Jataka Tales (Babbitt, 1922) | Pan-India | 21 |
| Indian Fairy Tales (Stokes, 1879) | North India | 30 |

Each story was extracted, cleaned, and structured from the original Gutenberg text using a custom parser (`data_generation/build_dataset.py`) that handles varying contents-list formats, footnotes, and closing formulas across books.

## Architecture

```
User query
   │
   ▼
RAGAgent ── translates non-English queries, retrieves the best-matching
   │         story from a Chroma vector DB (multilingual embeddings),
   │         then narrates it faithfully in the target language (Gemini)
   ▼
TTSAgent ── converts the narration to speech (gTTS)
   │
ImageAgent ── writes a scene prompt and generates an illustration
   │           (Hugging Face Inference API)
   ▼
ValidationAgent ── (optional) judges faithfulness against the source
                    tale (Gemini)
```

**LLM roles are split by task**, balancing free-tier quota against reliability:
- **Gemini 2.5 Flash** — story narration and faithfulness validation (needs fluency and reliable instruction-following).
- **Ollama (Llama 3.1 8B, local)** — query translation and image-scene prompts (short, high-volume tasks that don't need Gemini's quota).
- **Hugging Face Inference API (FLUX.1-schnell)** — image generation (Gemini's free tier has no image quota).

## Retrieval evaluation

Retrieval was evaluated on gold-set queries covering all 213 stories (559 English, 213 Hindi, 213 Telugu — 985 total) comparing chunk-scoring strategies:

| Scoring method | English Hit@1 | Hindi Hit@1 | Telugu Hit@1 |
|---|---|---|---|
| sum (naive) | 0.31 | 0.15 | 0.11 |
| max | 0.41 | 0.18 | 0.17 |
| **top2 (used)** | **0.41** | **0.20** | **0.18** |

Key findings:
- Summing all chunk scores biases toward longer stories; scoring by the best 1–2 chunks corrects this.
- Non-English queries are translated to English before retrieval, which measurably improved Hindi/Telugu retrieval (Telugu Hit@1 rose from ~0.05 to ~0.18).
- Cross-language retrieval remains noticeably weaker than English — a known, documented limitation of the local translation step, not silently hidden.

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Create a `.env` file:

```
GOOGLE_API_KEY=your_gemini_api_key
HF_TOKEN=your_huggingface_token       # needs "Inference" permission
```

[Ollama](https://ollama.com) must be installed locally for translation/scene-prompt generation:

```bash
ollama pull llama3.1:8b
```

Build the vector index (run once, or after changing `data/stories.jsonl`):

```bash
python ingest.py --reset
```

## Running the app

**Option A — directly:**

```bash
streamlit run app.py
```

or from the command line:

```bash
python main.py
```

**Option B — via Docker (recommended, fully reproducible):**

```bash
docker compose up -d ollama
docker compose up ollama-pull
docker compose --profile ingest run --rm ingest
docker compose up --build app
```

Visit `http://localhost:8501`. The full pipeline — retrieval, Gemini narration, Ollama translation, gTTS audio, and Hugging Face image generation — has been tested end-to-end inside this container setup.

## Deployment

This app is designed to run locally or via Docker. It is **not deployed to a public URL**, by design: the translation and image-prompt steps depend on Ollama running a local 4.9GB LLM, which needs more RAM, disk, and CPU than free hosting tiers (Streamlit Community Cloud, Render, Railway, etc.) provide. Running it there would require either a paid cloud VM or rewriting those steps to rely entirely on hosted APIs instead of Ollama — a reasonable future extension, but out of scope here in favor of keeping local inference free and unlimited during development.

## Project structure

```
agents/            RAG, TTS, image, validation, and coordinator agents
config.py          All tunable settings (models, thresholds, providers)
data/stories.jsonl The cleaned 213-story dataset
data_generation/   Dataset-building and gold-set generation scripts
eval/              Retrieval evaluation and manual test scripts
utils/llm.py       Swaps between Gemini and Ollama per task
app.py / main.py   Streamlit and CLI entry points
```

## Known limitations

- **Cross-language retrieval** (Hindi/Telugu) is functional but noticeably weaker than English, due to translation quality from the local Llama model.
- **Image generation** depends on Hugging Face's free Inference API, which can be rate-limited or require a brief model "warm-up" on first use.
- **Local-model validation** (Ollama) was tested and found unreliable on long-document faithfulness comparisons; the validation agent uses Gemini instead for this reason.
- Several tales exist in more than one source book (e.g. two versions of "Punchkin"), which is expected given the historical overlap between these 19th-century collections.
