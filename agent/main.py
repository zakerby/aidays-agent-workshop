from langchain.agents import initialize_agent, AgentType
from langchain_community.llms import Ollama
from langchain_community.tools import Tool
import time

from tools.tools import check_logs_for_errors, restart_container, check_endpoint_health

def create_agent():
    try:
        llm = Ollama(
            base_url="http://localhost:11434",
            model="gemma2:2b"
        )

        tools = [
            Tool(
                name="check_logs",
                func=check_logs_for_errors,
                description="Check application logs for 500 errors"
            ),
            Tool(
                name="restart_webapp",
                func=restart_container,
                description="Restart the web application container"
            ),
            Tool(
                name="check_health",
                func=check_endpoint_health,
                description="Check if the webapp is responding"
            )
        ]

        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )

        return agent
    except Exception as e:
        print(f"Error creating agent: {e}")
        return None
    
def main():
    agent = create_agent()
    
    if agent:
        while True:
            try:
                response = agent.run(
                    """Monitor the web application:
                    1. Check if the application is responding
                    2. If not responding or if 500 errors are found in logs, restart the container
                    3. Report the status after actions taken
                    """
                )
                print(f"Agent response: {response}")
                
            except Exception as e:
                print(f"Error running agent: {e}")
            
            time.sleep(60)  # Wait 1 minute before next check


if __name__ == "__main__":
    main()