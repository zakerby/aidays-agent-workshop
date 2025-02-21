from smolagents import load_tool, CodeAgent, DuckDuckGoSearchTool
from dotenv import load_dotenv

from .llm.ollama import OllamaModel

load_dotenv()

ollama_model = OllamaModel("gemma:2b")

# create agent
agent = CodeAgent(
    model=ollama_model,
    tools=[DuckDuckGoSearchTool()],
    planning_interval=3
)

# run agent
res = agent.run(
    "Prompt"
)