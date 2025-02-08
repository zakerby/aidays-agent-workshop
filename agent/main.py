from langchain.agents import initialize_agent, AgentType
from langchain_community.llms import Ollama
from langchain_community.tools.shell.tool import ShellTool

def create_agent():
    try:
        # Initialize the LLM hosted on Ollama
        llm = Ollama(
            base_url="http://localhost:11434",  # Default Ollama port
            model="gemma2:2b"  # Specify the model you want to use
        )

        # Create shell tool with a safe command
        shell_tool = ShellTool()

        # Initialize the agent with the LLM and tool
        agent = initialize_agent(
            tools=[shell_tool],
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )

        return agent

    except Exception as e:
        print(f"Error creating agent: {e}")
        return None

def main():
    # Create the agent
    agent = create_agent()
    
    if agent:
        try:
            # Run a simple command through the agent
            response = agent.run(
                "What is the current directory? Use the shell command 'pwd' to find out."
            )
            print(f"Agent response: {response}")
            
        except Exception as e:
            print(f"Error running agent: {e}")

if __name__ == "__main__":
    main()