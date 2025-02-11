from typing import Optional
from langchain_ollama.llms import OllamaLLM
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import Tool,  StructuredTool
from langchain import hub
from langchain_core.prompts import PromptTemplate
import time
import argparse
from tools.tools import check_logs_for_errors, restart_container, check_endpoint_health, LogCheckInput, ContainerRestartInput, EndpointHealthInput

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

def get_llm(ollama_url: str, model_name: str) -> OllamaLLM:
    try:
        llm  = OllamaLLM(
            base_url=ollama_url,
            model=model_name,
            temperature=0.1
        )
        return llm
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        return None
    
def get_tools():
    # Define tools with more detailed descriptions
    tools = [
        StructuredTool(
            name="check_health",
            func=check_endpoint_health,
            description="Check if the webapp is responding at the specified URL. Returns HTTP status code.",
            args_schema=EndpointHealthInput
        ),
        StructuredTool(
            name="check_logs",
            func=check_logs_for_errors,
            description="Check application logs for 500 errors in the specified container.",
            args_schema=LogCheckInput
        ),
        StructuredTool(
            name="restart_webapp",
            func=restart_container,
            description="Restart the specified web application container.",
            args_schema=ContainerRestartInput
        )
    ]
    return tools  

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
    
def main():
    parser = argparse.ArgumentParser(description='AI Monitoring Agent')
    parser.add_argument('--llm_url', default='http://localhost:11434', help='LLM base URL')
    parser.add_argument('--model', default='gemma:2b', help='LLM model name')
    parser.add_argument('--interval', type=int, default=60, help='Monitoring interval in seconds')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--monitored_container', default='aidays-agent-logs-analysis-python-app', help='Name of the container to monitor')
    parser.add_argument('--webapp_url', default='http://localhost:5000', help='URL of the web application to monitor')
    
    args = parser.parse_args()
    
    print(f"Starting monitoring agent with model: {args.model} on {args.llm_url}")
    print(f"Monitoring interval: {args.interval} seconds")
    
    agent = create_agent(args.llm_url, args.model)
    run_agent(agent, args.monitored_container, args.webapp_url, args.interval)

if __name__ == "__main__":
    main()