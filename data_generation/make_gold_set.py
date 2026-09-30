import os, sys, json, random, time, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pydantic import BaseModel, Field
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm import get_llm
import config

class Queries(BaseModel):
    en: list[str] = Field(description="3 different English search queries")
    hi: str = Field(description="Hindi translation of the first English query")
    te: str = Field(description="Telugu translation of the first English query")

PROMPT = """Write 3 short search queries (5-12 words each) a user might type to find this folk tale.
Describe the plot, characters or theme. Do NOT use the title or any character's proper name.
Then translate the FIRST query into Hindi and Telugu.

TALE:
{text}"""

p = argparse.ArgumentParser()
p.add_argument("--n", type=int, default=100)
p.add_argument("--sleep", type=float, default=6.0)
p.add_argument("--out", default="data/eval/gold.jsonl")
a = p.parse_args()

os.makedirs(os.path.dirname(a.out), exist_ok=True)
stories = [json.loads(l) for l in open(config.STORIES_PATH, encoding="utf-8")]
stories = [s for s in stories if len(s["text"]) >= 1000]

done = set()
if os.path.exists(a.out):
    done = {json.loads(l)["story_id"] for l in open(a.out, encoding="utf-8")}

remaining = [s for s in stories if s["id"] not in done]
sample = random.Random(42).sample(remaining, min(a.n, len(remaining)))
print(f"{len(done)} stories already done, {len(remaining)} remaining, sampling {len(sample)} now")

chain = get_llm(temperature=0.7).with_structured_output(Queries)

with open(a.out, "a", encoding="utf-8") as out:
    for i, s in enumerate(sample, 1):
        if s["id"] in done:
            continue
        text = s["text"][:2500] + (" ... " + s["text"][-1000:] if len(s["text"]) > 3500 else "")
        try:
            for attempt in range(4):
                try:
                    q = chain.invoke(PROMPT.format(text=text))
                    break
                except Exception as e:
                    if "RESOURCE_EXHAUSTED" in str(e) and attempt < 3:
                        wait = 30 * (attempt + 1)
                        print(f"  rate limited, waiting {wait}s...")
                        time.sleep(wait)
                    else:
                        raise
        except Exception as e:
            print("skip", s["id"], type(e).__name__, str(e)[:120])
            continue
        for lang, qs in (("en", q.en[:3]), ("hi", [q.hi]), ("te", [q.te])):
            for x in qs:
                out.write(json.dumps({"query": x, "lang": lang, "story_id": s["id"],
                                      "title": s["title"]}, ensure_ascii=False) + "\n")
        out.flush()
        print(f"{i}/{len(sample)} {s['id']}")
        time.sleep(a.sleep)