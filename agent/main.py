from smolagents import load_tool, CodeAgent, DuckDuckGoSearchTool
from dotenv import load_dotenv

from .llm.ollama import OllamaModel
from tools.agent_tools import get_tools

load_dotenv()

ollama_model = OllamaModel("gemma:2b")

# create agent
agent = CodeAgent(
    model=ollama_model,
    tools=get_tools(),
    planning_interval=3
)

# run agent
res = agent.run(
    "Prompt"
)