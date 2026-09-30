import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.image_agent import ImageAgent

story = """Once, a wicked magician named Punchkin hid his life inside a little green parrot,
deep in a jungle guarded by thousands of genii. A brave prince flew there on eagle-back,
seized the parrot, and returned to confront the magician at his palace gate."""

agent = ImageAgent()
path = agent.generate_image(story)
print("Result:", path)