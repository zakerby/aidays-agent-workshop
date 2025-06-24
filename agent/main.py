import time
import argparse
from langchain.agents import AgentExecutor

from smolagents import CodeAgent
from dotenv import load_dotenv

from .llm.ollama import OllamaModel
from tools.agent_tools import get_monitoring_tools

load_dotenv()

AGENT_PROMPT = """
    Monitor the Docker container health:
        1. Check container logs for HTTP 500 errors
        2. Check container metrics (CPU, memory, network usage)
        3. If issues are found:
        - On first detection: restart the container
        - If issues persist after restart: notify support team
        4. Report the current status and any actions taken
"""

def create_monitoring_agent():
    ollama_model = OllamaModel('http://localhost:11434', "gemma:2b")
    
    agent = CodeAgent(
        model=ollama_model,
        tools=get_monitoring_tools(),
        planning_interval=3
    )
    return agent

def main():
    agent = create_monitoring_agent()
    issues_count = 0
    
    print("Starting container monitoring...")
    
    # first ensure that the webapp is running
    if agent.run(f"docker ps | grep {agent.webapp_container}") == "":
        print(f"Web application container {agent.webapp_container} is not running, nothing  to do")
        return
    
    while True:
        try:
            response = agent.run(AGENT_PROMPT)
            
            # Track issues and escalate if needed
            if "restarted" in str(response):
                issues_count += 1
                if issues_count >= 3:
                    agent.run("Notify support team about persistent issues")
                    issues_count = 0
            else:
                issues_count = 0
            
            print(f"\nMonitoring cycle complete: {response}")
            
        except Exception as e:
            print(f"Error during monitoring: {e}")
        
        time.sleep(300)  # Wait 5 minutes between checks


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

if __name__ == "__main__":
    main()