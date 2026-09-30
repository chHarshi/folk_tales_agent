from pydantic import BaseModel, Field
from utils.llm import get_llm
import config

class Verdict(BaseModel):
    faithfulness: int = Field(description="1-5: does the story only contain events found in the source tale?")
    completeness: int = Field(description="1-5: does it have a clear beginning, middle, and end?")
    has_moral: bool
    invented_elements: list[str] = Field(description="Plot points or characters NOT in the source; empty list if none")

JUDGE_PROMPT = """Compare the retold STORY against the SOURCE tale and grade it honestly.

SOURCE:
{context}

STORY:
{story}"""

class ValidationAgent:
    def __init__(self):
        self.judge = get_llm("gemini", temperature=0).with_structured_output(Verdict)

    def validate(self, story, context):
        v = self.judge.invoke(JUDGE_PROMPT.format(story=story, context=context))
        result = v.model_dump()
        result["passed"] = v.faithfulness >= 4 and v.has_moral and v.completeness >= 3
        return result