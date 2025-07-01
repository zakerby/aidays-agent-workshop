from smolagents import CodeAgent, ToolCallingAgent, LiteLLMModel, tool
import requests


# LiteLLMModel is a wrapper around the LiteLLM API, 
# which is an OpenAI compatible API for running LLMs
model = LiteLLMModel(
    api_base="http://localhost:11434",  # replace with remote open-ai compatible server if necessary
    model_id="ollama_chat/llama3.2",
    # ollama default is 2048 which will often fail horribly. 8192 works for easy tasks, more is better. 
    num_ctx=8192,  
)

@tool
def get_current_weather_dummy(location: str) -> str:
    """
    Get current weather for a given location.
    This is a dummy function that simulates the behavior of the actual weather function.
    
    Args:
        location: a string representing the location, e.g., "Brest", "Lorient", or "Paris".
        
    Returns:
        A string with the current weather in the given location.
    """
    return f"Current weather in {location}: 25°C, wind speed 10 km/h (dummy response)"

@tool
def get_current_weather(location: str) -> str:
    """
    Get current weather for a given location.

    Args:
        location: the location, e.g., "New York", "London", or "Tokyo".
    Returns:
        A string with the current weather in the given location.
    """
    # Step 1: Geocode location
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {"name": location, "count": 1, "language": "en", "format": "json"}
    geo_resp = requests.get(geo_url, params=geo_params)
    geo_data = geo_resp.json()
    if not geo_data.get("results"):
        return f"Could not find location: {location}"

    lat = geo_data["results"][0]["latitude"]
    lon = geo_data["results"][0]["longitude"]

    # Step 2: Get weather forecast
    units = "celsius"
    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "temperature_unit": units,
    }
    weather_resp = requests.get(weather_url, params=weather_params)
    weather_data = weather_resp.json()
    if "current_weather" not in weather_data:
        return "Weather data unavailable."

    temp = weather_data["current_weather"]["temperature"]
    wind = weather_data["current_weather"]["windspeed"]
    unit = "°C"
    return f"Current weather in {location}: {temp}{unit}, wind speed {wind} km/h"

agent = ToolCallingAgent(model=model, tools=[get_current_weather_dummy], verbosity_level=2)

print(f"""I am a simple agent that can answer questions about the current weather.
      Type 'exit' or 'quit' to stop.""")

while True:
    try:
        user_input = input("Ask a question: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        
        # Add control here to ensure the agent can handle the input
        # Here the agent can only handle the weather question
        if "weather" not in user_input.lower():
            print("I can only answer questions about the current weather. Please ask something related to weather.")
            continue
           
        response = agent.run(user_input)
        print("Response:", response)
        print("-----------------------------------")
    except KeyboardInterrupt:
        print("\nExiting...")
        break
    except Exception as e:
        print("Error:", e)
