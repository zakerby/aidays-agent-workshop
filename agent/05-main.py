from smolagents import CodeAgent, LiteLLMModel, ToolCallingAgent
import argparse

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

    return agent

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
        f"""
        You are an autonomous monitoring agent for a web application running in a Docker container.

        Your monitoring loop is as follows:

        1. Use the `check_endpoint_health` tool on {args.webapp_url}.
        2. If the result indicates the endpoint is healthy (status 200 OK), wait {args.interval} seconds and repeat step 1.
        3. If the result indicates the endpoint is unhealthy (status not 200 OK or 500 error):
            a. Use the `get_container_logs` tool on the container '{args.monitored_container}' to retrieve recent logs.
            b. Analyze the logs for signs of a crash or error (look for keywords like "error", "exception", "crash", or stack traces).
            c. If a crash or error is detected in the logs:
                i. Use the `restart_container` tool on '{args.monitored_container}'.
                ii. After restarting, use the `check_endpoint_health` tool again on {args.webapp_url}.
                iii. If the endpoint is now healthy, resume monitoring as in step 1.
                iv. If the endpoint is still unhealthy, use the `send_slack_alert` tool to notify the team with a summary of the issue.
            d. If no crash or error is detected in the logs, use the `send_slack_alert` tool to notify the team with the log output and health check result.

        Always use the appropriate tool for each step and provide clear, concise output for each action.
        """
    )

if __name__ == "__main__":
    main()