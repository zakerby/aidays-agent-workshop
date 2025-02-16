from typing import Dict, Any
from langchain_community.tools.shell.tool import ShellTool
from langchain_core.tools import StructuredTool
import requests
from pydantic import BaseModel, Field

class LogCheckInput(BaseModel):
    container_name: str = Field(
        default="webapp",
        description="Name of the Docker container to check"
    )

class ContainerRestartInput(BaseModel):
    container_name: str = Field(
        default="webapp",
        description="Name of the Docker container to restart"
    )

class EndpointHealthInput(BaseModel):
    url: str = Field(
        default="http://localhost:8080",
        description="URL to check for health status"
    )

def check_endpoint_health(url: str = "http://localhost:8080") -> str:
    """Check if a web endpoint is responding."""
    try:
        response = requests.get(url, timeout=5)
        return f"Status code: {response.status_code}"
    except requests.RequestException as e:
        return f"Error accessing webapp: {e}"

def check_logs_for_errors(container_name: str = "webapp") -> str:
    """Check Docker logs for 500 errors."""
    try:
        cmd = f"docker logs {container_name} 2>&1 | grep '500'"
        result = ShellTool().run(cmd)
        return result if result else "No 500 errors found"
    except Exception as e:
        return f"Error checking logs: {str(e)}"

def restart_container(container_name: str = "webapp") -> str:
    """Restart a Docker container."""
    try:
        result = ShellTool().run(f"docker restart {container_name}")
        return f"Container {container_name} restarted successfully"
    except Exception as e:
        return f"Failed to restart container: {str(e)}"

def notify_team() -> str:
    """Send a notification to the team."""
    return "Team notified"
    
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