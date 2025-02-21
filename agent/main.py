from smolagents import CodeAgent
from dotenv import load_dotenv
import time

from .llm.ollama import OllamaModel
from tools.agent_tools import get_monitoring_tools

load_dotenv()

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
    
    while True:
        try:
            response = agent.run(
                """Monitor the Docker container health:
                1. Check container logs for HTTP 500 errors
                2. Check container metrics (CPU, memory, network usage)
                3. If issues are found:
                   - On first detection: restart the container
                   - If issues persist after restart: notify support team
                4. Report the current status and any actions taken
                """
            )
            
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

if __name__ == "__main__":
    main()