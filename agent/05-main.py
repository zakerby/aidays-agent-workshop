from smolagents import CodeAgent, LiteLLMModel, ToolCallingAgent
import time
import argparse

import docker

from tools.tools import get_tools

def get_model(llm_url: str, model_name: str = "ollama_chat/llama3.2") -> LiteLLMModel:
    return LiteLLMModel(
        model_id=model_name,
        api_base=llm_url,
        max_tokens=1024,
        temperature=0.1,
        top_p=0.95,
        top_k=40,
        stop=["\n\n"],
    )

def create_agent(llm_url: str, model: str) -> CodeAgent:
    """
        Create and return a CodeAgent instance with the specified LLM URL and model.
    """
    model = get_model(llm_url, model)
    agent = ToolCallingAgent(
        model=model, 
        tools=get_tools(),
        name="ai_monitoring_agent",
        description="An agent that monitors a web application and manages its health.",
        verbosity_level=2
    )
    
    manager_agent = CodeAgent(
        model=model,
        verbosity_level=2,
        name="ai_monitoring_manager_agent",
        description="An agent that manages other agents to monitor a web application.",
        managed_agents=[agent],
        tools=[]
    )
    
    return manager_agent

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='AI Monitoring Agent (smolagents)')
    parser.add_argument('--llm_url', default='http://localhost:11434', help='LLM base URL')
    parser.add_argument('--model', default='gemma:2b', help='LLM model name')
    parser.add_argument('--interval', type=int, default=60, help='Monitoring interval in seconds')
    parser.add_argument('--monitored_container', default='python-app', help='Name of the container to monitor')
    parser.add_argument('--webapp_url', default='http://localhost:5000', help='URL of the web application to monitor')
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    print(f"Starting monitoring agent (smolagents) with model: {args.model} on {args.llm_url}")
    print(f"Monitoring the app {args.monitored_container} at host {args.webapp_url}, polling every {args.interval} seconds")
    agent = create_agent(args.llm_url, args.model)
    
    agent.run(
        """
        Please monitor the web application:
            1. Check the health status at {webapp_url}
            2. If unhealthy, check logs for container '{monitored_container}'
            3. If needed, restart container '{monitored_container}'
            4. Verify the health status again
            5. If still unhealthy, escalate to the team
        """.format(webapp_url=args.webapp_url, monitored_container=args.monitored_container),
    )

if __name__ == "__main__":
    main()