from typing import Optional
from langchain_community.llms import Ollama
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import Tool
from langchain import hub
from langchain_core.prompts import PromptTemplate
import time
import argparse
from tools.tools import check_logs_for_errors, restart_container, check_endpoint_health

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

def get_llm(ollama_url: str, model_name: str) -> Ollama:
    try:
        llm  = Ollama(
            base_url=ollama_url,
            model=model_name,
            temperature=0.1
        )
        return llm
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        return None

def create_agent(ollama_url: str, model_name: str) -> Optional[AgentExecutor]:
    try:
        # Initialize the LLM with temperature setting
        llm = get_llm(ollama_url, model_name)

        # Define tools with more detailed descriptions
        tools = [
            Tool(
                name="check_health",
                func=check_endpoint_health,
                description="Use this first to check if the webapp is responding. Returns HTTP status code.",
                return_direct=True
            ),
            Tool(
                name="check_logs",
                func=check_logs_for_errors,
                description="Check application logs for 500 errors. Use this if health check fails.",
                return_direct=True
            ),
            Tool(
                name="restart_webapp",
                func=restart_container,
                description="Restart the web application container. Use this only if errors are found.",
                return_direct=True
            )
        ]

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
     
def run_agent(agent: AgentExecutor, interval: float) -> None:
    if not agent:
        print("Agent initialization failed. Exiting.")
        return

    while True:
        try:
            response = agent.invoke(
                {
                    "input": """Please monitor the web application:
                    1. Check the current health status
                    2. Review logs if there are issues
                    3. Take corrective actions if needed
                    4. Verify system health after any changes
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
    
def main():
    parser = argparse.ArgumentParser(description='AI Monitoring Agent')
    parser.add_argument('--llm_url', default='http://localhost:11434', help='LLM base URL')
    parser.add_argument('--model', default='gemma:2b', help='LLM model name')
    parser.add_argument('--interval', type=int, default=60, help='Monitoring interval in seconds')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    print(f"Starting monitoring agent with model: {args.model} on {args.llm_url}")
    print(f"Monitoring interval: {args.interval} seconds")
    
    agent = create_agent(args.llm_url, args.model)
    run_agent(agent, args.interval)

if __name__ == "__main__":
    main()