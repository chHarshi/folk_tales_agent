import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8")

from agents.rag_agent import RAGAgent
import config

QUERIES = [
    "a clever jackal tricks a crocodile",
    "story about a tiger and a brahman",
    "a wicked magician whose life is hidden in a parrot",
    "नक्क मगरमच्छ की कहानी" if False else "एक चालाक सियार और मगरमच्छ की कहानी",
    "నక్క మొసలి కథ",
    "tell me about cricket",
]

agent = RAGAgent()

# Usage 1: python eval/try_retrieval.py "your query"   -> full story, saved to outputs/test_story.txt
if len(sys.argv) > 1:
    q = " ".join(sys.argv[1:])
    r = agent.run(q)
    print(r["sources"])
    if r["story"]:
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        path = os.path.join(config.OUTPUT_DIR, "test_story.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(r["story"])
        print(r["story"][:800])
        print("...\nsaved to", path)
    sys.exit()

# Usage 2: python eval/try_retrieval.py   -> retrieval only, no LLM call
for q in QUERIES:
    needs_translation = any(ord(c) > 0x2FF for c in q)
    ranked, top = agent.rank_stories(q, agg="top2", translate=needs_translation)
    verdict = "ANSWER" if ranked and top >= config.MIN_RELEVANCE else "NO MATCH"
    print(f"\nQ: {q}\n   best chunk score {top:.2f} -> {verdict}")
    for sid, sc in ranked[:3]:
        s = agent.stories[sid]
        print(f"   {sc:.2f}  {s['title']}  [{s['source']}]")
        