from smolagents import CodeAgent, ToolCallingAgent, LiteLLMModel, tool
import requests

model = LiteLLMModel(
    model_id="ollama_chat/llama3.2",
    api_base="http://localhost:11434",  # replace with remote open-ai compatible server if necessary
    # ollama default is 2048 which will often fail horribly. 8192 works for easy tasks, more is better. Check https://huggingface.co/spaces/NyxKrage/LLM-Model-VRAM-Calculator to calculate how much VRAM this will need for the selected model.
    num_ctx=8192,  
)

@tool
def get_weather(location: str) -> str:
    """
    Get weather in the next days at given location.

    Args:
        location: the location
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

agent = ToolCallingAgent(tools=[get_weather], model=model, verbosity_level=2)

while True:
    try:
        user_input = input("Ask a question: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        
        response = agent.run(user_input)
        print("Response:", response)
    except KeyboardInterrupt:
        print("\nExiting...")
        break
    except Exception as e:
        print("Error:", e)
