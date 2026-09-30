import os, sys, json, re, statistics
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8")
from agents.rag_agent import RAGAgent

OFF_TOPIC = [
    "tell me about cricket", "how do I bake a chocolate cake", "what is the capital of France",
    "explain how a car engine works", "latest smartphone reviews", "how to invest in stocks",
    "python list comprehension example", "weather forecast for tomorrow",
    "who won the football world cup", "how to lose weight fast",
]

def key(t):
    return re.sub(r"[^a-z0-9 ]", "", t.lower()).strip()

agent = RAGAgent()
gold = [json.loads(l) for l in open("data/eval/gold.jsonl", encoding="utf-8")]
title_of = {sid: key(s["title"]) for sid, s in agent.stories.items()}

def evaluate(agg, lang):
    rows = [g for g in gold if g["lang"] == lang]
    if not rows:
        return None
    hits = {m: {1: 0, 3: 0, 5: 0} for m in ("strict", "lenient")}
    rr = {"strict": 0.0, "lenient": 0.0}
    for g in rows:
        ranked, _ = agent.rank_stories(g["query"], k=20, agg=agg,
                                       translate=(g["lang"] != "en"))
        ids = [sid for sid, _ in ranked]
        target = title_of[g["story_id"]]
        for m in hits:
            ok = (lambda sid: sid == g["story_id"]) if m == "strict" else (lambda sid: title_of[sid] == target)
            pos = next((i + 1 for i, sid in enumerate(ids) if ok(sid)), None)
            if pos:
                rr[m] += 1 / pos
                for k in hits[m]:
                    hits[m][k] += pos <= k
    n = len(rows)
    return n, hits, rr

print(f"{'agg':5} {'lang':4} {'n':>4} | {'strict H@1':>10} {'H@3':>6} {'H@5':>6} {'MRR':>6} | {'lenient H@1':>11} {'H@3':>6} {'H@5':>6} {'MRR':>6}")
for agg in ("sum", "max", "top2"):
    for lang in ("en", "hi", "te"):
        r = evaluate(agg, lang)
        if not r:
            continue
        n, h, rr = r
        s, l = h["strict"], h["lenient"]
        print(f"{agg:5} {lang:4} {n:>4} | {s[1]/n:>10.2f} {s[3]/n:>6.2f} {s[5]/n:>6.2f} {rr['strict']/n:>6.2f} | "
              f"{l[1]/n:>11.2f} {l[3]/n:>6.2f} {l[5]/n:>6.2f} {rr['lenient']/n:>6.2f}")

def top_scores(queries, translate=False):
    return [agent.rank_stories(q, k=10, translate=translate)[1] for q in queries]

print("\nBest-chunk score distributions (for choosing MIN_RELEVANCE):")
for lang in ("en", "hi", "te"):
    sc = top_scores([g["query"] for g in gold if g["lang"] == lang], translate=(lang != "en"))
    if sc:
        print(f"  on-topic {lang}: min {min(sc):.2f}  median {statistics.median(sc):.2f}  max {max(sc):.2f}")
neg = top_scores(OFF_TOPIC)
print(f"  off-topic en: min {min(neg):.2f}  median {statistics.median(neg):.2f}  max {max(neg):.2f}")