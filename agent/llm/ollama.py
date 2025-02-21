import ollama
from dataclasses import dataclass

@dataclass
class Message:
    content: str  # Required attribute for smolagents

class OllamaModel:
    def __init__(self, model_name):
        self .model_name = model_name
        self.client = ollama.Client(model_name)
        
    def __call__(self, messages, **kwargs):
        formatted_msgs = []
        for msg in messages:
            if isinstance(msg, str):
                formatted_msgs.append({
                    "role": "user",
                    "content": msg
                })
            elif isinstance(msg, dict):
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if isinstance(content, list):
                    content = " ".join(part.get("text", "") for part in content if isinstance(part, dict) and "text" in part)                
                formatted_msgs.append({
                    "role": role if role in ['user', 'assistant', 'system', 'tool'] else 'user',
                    "content": content
                })
            else:
                formatted_msgs.append({
                    "role": "user",
                    "content": str(msg)
                })
        response = self.client.chat(
            model=self.model_name,
            messages=formatted_msgs,
            options={'temperature': 0.5, 'stream': False}
        )
        
        return Message(
            content=response.get("message", {}).get("content", "")
        )
      