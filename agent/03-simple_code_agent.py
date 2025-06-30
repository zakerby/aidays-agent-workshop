from smolagents import CodeAgent, LiteLLMModel, tool

model = LiteLLMModel(
    model_id="ollama_chat/llama3.2",
    api_base="http://localhost:11434",  # replace with remote open-ai compatible server if necessary
    # ollama default is 2048 which will often fail horribly. 8192 works for easy tasks, more is better. Check https://huggingface.co/spaces/NyxKrage/LLM-Model-VRAM-Calculator to calculate how much VRAM this will need for the selected model.
    num_ctx=8192,
)

@tool
def calc_tool(expression: str) -> str:
    """
    Calculate a mathematical expression.

    Args:
        expression: the mathematical expression to calculate
    Returns:
        The result of the calculation as a string.
    """
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error calculating expression '{expression}': {str(e)}"



agent = CodeAgent(
    model=model,
    tools=[calc_tool],
    verbosity_level=2,
)

while True:
    try:
        user_input = input("Enter your query: ")
        if user_input.lower() == "exit":
            break
        response = agent.run(user_input)
        print(f"Agent response: {response}")
    except KeyboardInterrupt:
        print("\nExiting...")
        break
    except Exception as e:
        print(f"An error occurred: {e}")