
from typing import Optional

from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from langchain_core.prompts import PromptTemplate

from agent.llm import get_llm
from tools.tools import get_tools


MONITORING_PROMPT = PromptTemplate.from_template(
    """You are a system monitoring agent responsible for maintaining a web application's health.

    When monitoring, always follow these steps in order:
    1. Check the application's health status first
    2. If unhealthy or unreachable, check the logs for errors
    3. If errors are found or the app is down, restart the container
    4. Verify the application is healthy after any actions
    
    Current task: {input}
    
    Think through this step-by-step:
    1) First, what is the current state of the system?
    2) What actions, if any, need to be taken?
    3) How can we verify the system is healthy?
    """
)


def create_agent(ollama_url: str, model_name: str) -> Optional[AgentExecutor]:
    try:
        # Initialize the LLM with temperature setting
        llm = get_llm(ollama_url, model_name)

        # Define tools with more detailed descriptions
        tools = get_tools()

        # Get base prompt from LangChain hub and combine with custom prompt
        base_prompt = hub.pull("hwchase17/react")
        prompt = base_prompt.partial(
            system_message=MONITORING_PROMPT.template
        )

        # Create the agent with the React framework
        agent = create_react_agent(
            llm=llm,
            tools=tools,
            prompt=prompt
        )

        # Create the agent executor with additional settings
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
            early_stopping_method="generate"
        )

    except Exception as e:
        print(f"Error creating agent: {e}")
        return None