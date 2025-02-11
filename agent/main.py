from typing import Optional
from langchain.agents import AgentExecutor
import time
import argparse

from llm.agent import create_agent


def run_agent(agent: AgentExecutor, monitored_container: str, webapp_url: str,  interval: float) -> None:
    if not agent:
        print("Agent initialization failed. Exiting.")
        return

    while True:
        try:
            response = agent.invoke(
                {
                    "input": """Please monitor the web application:
                    1. Check the health status at {webapp_url}
                    2. If unhealthy, check logs for container '{monitored_container}'
                    3. If needed, restart container '{monitored_container}'
                    4. Verify the health status again
                    """
                }
            )
            # Extract and log the agent's reasoning and actions
            if isinstance(response, dict):
                print(f"\nAgent Reasoning: {response.get('intermediate_steps', '')}")
                print(f"Final Response: {response.get('output', '')}")
            else:
                print(f"\nAgent Response: {response}")
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
            break
        except Exception as e:
            print(f"Error running agent: {e}")
        
        time.sleep(interval)  # Wait 1 minute before next check

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='AI Monitoring Agent')
    parser.add_argument('--llm_url', default='http://localhost:11434', help='LLM base URL')
    parser.add_argument('--model', default='gemma:2b', help='LLM model name')
    parser.add_argument('--interval', type=int, default=60, help='Monitoring interval in seconds')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--monitored_container', default='aidays-agent-logs-analysis-python-app', help='Name of the container to monitor')
    parser.add_argument('--webapp_url', default='http://localhost:5000', help='URL of the web application to monitor')
    
    args = parser.parse_args()
    
    return args
    
def main() -> None:
    args = parse_args()
    
    print(f"Starting monitoring agent with model: {args.model} on {args.llm_url}")
    print(f"Monitoring the app {args.monitored_container} at host {args.webapp_url}, polling every {args.interval} seconds")
    
    agent = create_agent(args.llm_url, args.model)
    run_agent(agent, args.monitored_container, args.webapp_url, args.interval)

if __name__ == "__main__":
    main()