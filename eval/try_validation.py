import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.rag_agent import RAGAgent
from agents.validation_agent import ValidationAgent

rag = RAGAgent()
validator = ValidationAgent()

result = rag.run("a wicked magician whose life is hidden in a parrot", "en")
print("Story generated. Validating...")

t0 = time.time()
verdict = validator.validate(result["story"], result["context"])
print(f"[TIMING] validation took {time.time() - t0:.1f}s")
print(verdict)