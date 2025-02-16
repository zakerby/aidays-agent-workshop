from langchain.agents import AgentExecutor
from langgraph.graph import Graph
import time
import argparse

from llm.agent import create_agent

def get_prompt(webapp_url: str, monitored_container: str) -> str:
    return f"""
        Please monitor the web application:
        1. Check the health status at {webapp_url}
        2. If unhealthy, check logs for container '{monitored_container}'
        3. If needed, restart container '{monitored_container}'
        4. Verify the health status again
    """

def run_agent(agent: Graph, monitored_container: str, webapp_url: str, interval: float) -> None:
    if not agent:
        print("Agent initialization failed. Exiting.")
        return

    while True:
        try:
            # Initialize state
            initial_state = {
                "messages": [],
                "next": "check_health",
                "health_status": "",
                "logs": "",
                "actions_taken": []
            }
            
            # Run the workflow
            result = agent.invoke(initial_state)
            
            # Log results
            print("\n Monitoring Cycle Results:")
            print(f"Health Status: {result['health_status']}")
            print(f"Actions Taken: {', '.join(result['actions_taken'])}")
            if result['logs']:
                print(f"Logs: {result['logs']}")
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
            break
        except Exception as e:
            print(f"Error running agent: {e}")
        
        time.sleep(interval)
        
def parse_args() -> argparse.Namespace:
    """
        Parse command line arguments
        Parameters:
            llm_url: str - LLM base URL
            model: str - LLM model name
            interval: int - Monitoring interval in seconds
            verbose: bool - Enable verbose output
            monitored_container: str - Name of the container to monitor
            webapp_url: str - URL of the web application to monitor
        Returns:
            argparse.Namespace - Parsed arguments
    """
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