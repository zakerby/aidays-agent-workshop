from langchain_ollama.llms import OllamaLLM

def get_llm(ollama_url: str, model_name: str, llm_type='local') -> OllamaLLM:
    if llm_type == 'local':
        return get_ollama(ollama_url, model_name)
        

def get_ollama(ollama_url: str, model_name: str):
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