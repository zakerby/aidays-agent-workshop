from langchain.agents import initialize_agent, AgentType
from langchain_community.llms import Ollama
from langchain_community.tools import Tool
import time
import argparse


from tools.tools import check_logs_for_errors, restart_container, check_endpoint_health

def create_agent(ollama_url, model_name):
    try:
        llm = Ollama(
            base_url=ollama_url,
            model=model_name
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
    
def run_agent(agent):    
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


    
def main():
    parser = argparse.ArgumentParser(description='Monitoring agent')
    parser.add_argument('--llm_url', default='http://localhost:11434', help='LLM base URL')
    parser.add_argument('--model', default='gemma2:2b', help='LLM model')
    
    args = parser.parse_args()
    agent = create_agent(args.llm_url, args.model)
    
    run_agent(agent)
    

if __name__ == "__main__":
    main()