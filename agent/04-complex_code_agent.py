from smolagents import CodeAgent, LiteLLMModel, Tool
from duckduckgo_search import DDGS
import subprocess
import tempfile
import os


model = LiteLLMModel(
    model_id="ollama_chat/llama3.2",
    api_base="http://localhost:11434",  # replace with remote open-ai compatible server if necessary
    # ollama default is 2048 which will often fail horribly. 8192 works for easy tasks, more is better. Check https://huggingface.co/spaces/NyxKrage/LLM-Model-VRAM-Calculator to calculate how much VRAM this will need for the selected model.
    num_ctx=8192,
)

class RunCodeTool(Tool):
    name = "run_code"
    description = "Execute Python code and return output"
    
    inputs = {
        "code": {
            "type": "string",
            "description": "The Python code to execute"
        }
    }
    
    output_type = "string"
    
    def forward(self, code: str) -> str:
        """
        Execute the provided Python code and return the output or error message.
        
        Args:
            code (str): The Python code to execute.
        
        Returns:
            str: The output of the executed code or an error message.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name
        try:
            result = subprocess.run(['python', temp_path], capture_output=True, text=True, timeout=10)
            return result.stdout or result.stderr
        finally:
            os.remove(temp_path)


class SearchDocsTool(Tool):
    name = "search_docs"
    description = "Search Python documentation for relevant information"
    
    inputs = {
        "query": {
            "type": "string",
            "description": "The search query to find relevant Python documentation"
        }
    }
    
    output_type = "string"
    
    def forward(self, query: str) -> str:
        """
        Search the Python documentation for the given query.
        
        Args:
            query (str): The search query.
        
        Returns:
            str: The search results from the Python documentation.
        """
        with DDGS() as ddgs:
            results = ddgs.text(f"{query} site:docs.python.org", max_results=3)
            return "\n".join([r['body'] for r in results])


class SaveCodeTool(Tool):
    name = "save_code"
    description = "Save generated code to a file"
    
    inputs = {
        "code": {
            "type": "string",
            "description": "The code to save to a file"
        }
    }
    
    output_type = "string"
    
    def forward(self, code: str) -> str:
        """
        Save the provided code to a file.
        
        Args:
            code (str): The code to save.
        
        Returns:
            str: Confirmation message with the file path.
        """
        path = "generated_code.py"
        with open(path, "w") as f:
            f.write(code)
        return f"Code saved to {path}"



run_code_tool = RunCodeTool()
search_docs_tool = SearchDocsTool()
save_code_tool = SaveCodeTool()

tools = [run_code_tool, search_docs_tool, save_code_tool]

agent = CodeAgent(
    model=model,
    tools=tools,
    verbosity_level=2,
)

while True:
    try:
        user_input = input("Enter your query related to programming: ")
        if user_input.lower() == "exit":
            break
        response = agent.run(user_input)
        print(f"Agent response: {response}")
    except KeyboardInterrupt:
        print("\nExiting...")
        break
    except Exception as e:
        print(f"An error occurred: {e}")