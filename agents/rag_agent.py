import json
from collections import defaultdict
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from utils.llm import get_llm
import config
from langchain_core.prompts import PromptTemplate as PT

TRANSLATE_PROMPT = PT.from_template(
    "Translate this search query into English. Reply with ONLY the translation, nothing else.\n\nQuery: {query}"
)
PROMPT = PromptTemplate.from_template("""
You are an Indian folk storyteller.

Retell the folk tale below in {language}, in a warm, natural storytelling voice.
Rules:
- Use ONLY the characters, events and outcome present in the tale. Do not invent new plot points.
- Keep the full arc of the story — beginning, middle, end — but tell it concisely. Aim for 300-450 words. Skip minor repetition and side details from the original; keep only what matters to the plot.
- Modernise the old-fashioned wording only, not the plot.
- Output ONLY the story itself: no preamble, no title, no markdown, no "The End".
- End with one line starting with "Moral:" (written in {language}).

Tale title: {title}
Tale text:
{context}

User request: {question}

Story:
""")


class RAGAgent:
    def __init__(self):
        self.vectordb = Chroma(
            collection_name=config.COLLECTION,
            embedding_function=HuggingFaceEmbeddings(model_name=config.EMBED_MODEL),
            persist_directory=config.PERSIST_DIR,
            collection_metadata={"hnsw:space": "cosine"},
        )
        with open(config.STORIES_PATH, encoding="utf-8") as f:
            self.stories = {s["id"]: s for s in map(json.loads, f)}
        self.llm = get_llm(config.STORY_LLM_PROVIDER, temperature=0.4)
        self.chain = PROMPT | self.llm
        self.translate_llm = get_llm(config.TRANSLATE_LLM_PROVIDER, temperature=0)
        self.translate_chain = TRANSLATE_PROMPT | self.translate_llm

    def to_english(self, query):
        try:
            return self.translate_chain.invoke({"query": query}).content.strip()
        except Exception:
            return query

    def rank_stories(self, query, k=10, agg="sum", translate=False):
        q = self.to_english(query) if translate else query
        results = self.vectordb.similarity_search_with_relevance_scores(q, k=k)
        if not results:
            return [], 0.0
        by_story = defaultdict(list)
        for doc, score in results:
            by_story[doc.metadata["story_id"]].append(max(score, 0))
        if agg == "max":            # best single chunk
            scores = {s: max(v) for s, v in by_story.items()}
        elif agg == "top2":         # best two chunks, so length can't dominate
            scores = {s: sum(sorted(v, reverse=True)[:2]) for s, v in by_story.items()}
        else:                       # "sum": every chunk in the top-k counts
            scores = {s: sum(v) for s, v in by_story.items()}
        ranked = sorted(scores.items(), key=lambda x: -x[1])
        return ranked, results[0][1]

    def retrieve_story(self, query, k=10):
        needs_translation = any(ord(c) > 0x2FF for c in query)
        ranked, top_score = self.rank_stories(query, k, agg="top2", translate=needs_translation)
        if not ranked or top_score < config.MIN_RELEVANCE:
            return None
        story_id = ranked[0][0]
        s = self.stories[story_id]
        return {"story_id": story_id, "title": s["title"], "source": s["source"],
                "region": s["region"], "text": s["text"], "score": top_score}

    def run(self, query, language="en"):
        hit = self.retrieve_story(query)
        if hit is None:
            return {"story": None, "context": "", "sources": [], "found": False}
        story = self.chain.invoke({
            "language": config.LANG_NAMES.get(language, "English"),
            "title": hit["title"], "context": hit["text"], "question": query,
        }).content
        story = self._extract_story(story)
        return {"story": story, "context": hit["text"], "found": True,
                "sources": [{"title": hit["title"], "source": hit["source"],
                             "region": hit["region"], "score": round(hit["score"], 3)}]}
    @staticmethod
    def _extract_story(text):
        text = text.strip()
        lines = text.split("\n", 1)
        if lines[0].rstrip().endswith(":") and len(lines) > 1:
            text = lines[1].lstrip()
        return text