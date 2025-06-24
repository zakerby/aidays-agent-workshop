from smolagents import tool
import docker

@tool
def check_endpoint_health(url: str = "http://localhost:8080") -> str:
    """
    Check the health status of a web application endpoint.
    
    Args:
        url (str): The URL of the web application endpoint to check.
        
    Returns:
        str: The health status of the endpoint.
    """
    import requests
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return f"Endpoint {url} is healthy."
        else:
            return f"Endpoint {url} returned status code {response.status_code}."
    except requests.exceptions.RequestException as e:
        return f"Error checking endpoint {url}: {str(e)}"

@tool
def get_container_status(container_name: str) -> str:
    """
    Check the status of a Docker container.
    
    Args:
        container_name (str): The name of the Docker container to check.
        
    Returns:
        str: The status of the container (e.g., running, stopped, etc.).
    """
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        return f"Container '{container_name}' is {container.status}."
    except docker.errors.NotFound:
        return f"Container '{container_name}' not found."
    except Exception as e:
        return f"Error checking container status: {str(e)}"
    
@tool
def get_recent_logs(container_name: str, lines: int = 100) -> str:
    """
    Fetch the most recent logs from a Docker container.
        
    Args:
        container_name (str): The name of the Docker container to fetch logs from.
        lines (int): The number of log lines to retrieve (default is 100).
        
    Returns:
        str: The recent logs from the container.
    """
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        logs = container.logs(tail=lines).decode('utf-8')
        return logs if logs else "No logs found."
    except docker.errors.NotFound:
        return f"Container '{container_name}' not found."
    except Exception as e:
        return f"Error fetching logs: {str(e)}"
    
@tool
def check_resource_usage() -> str:
    """
    Check the resource usage of the system.
    
    Args:
        None
    Returns:
        str: A summary of resource usage (CPU, memory, disk, etc.).
    """
    try:
        client = docker.from_env()
        stats = client.stats(stream=False)
        cpu_usage = stats['cpu_stats']['cpu_usage']['total_usage']
        memory_usage = stats['memory_stats']['usage']
        disk_usage = stats['blkio_stats']['io_service_bytes_recursive']
        
        return (f"CPU Usage: {cpu_usage} nanoseconds\n"
                f"Memory Usage: {memory_usage} bytes\n"
                f"Disk Usage: {disk_usage}")
    except Exception as e:
        return f"Error checking resource usage: {str(e)}"
    
@tool
def send_slack_alert(message: str) -> str:
    """
    Send an alert message to a Slack channel.
    
    Args:
        message (str): The alert message to send.
        
    Returns:
        str: Confirmation of the alert sent.
    """
    pass  # Implement the logic to send a Slack alert

@tool
def run_self_heal_script(script_name: str) -> str: 
    """Run a self-healing script to fix issues."""
    try:
        client = docker.from_env()
        container = client.containers.get(script_name)
        container.restart()
        return f"Self-heal script '{script_name}' executed successfully."
    except docker.errors.NotFound:
        return f"Container '{script_name}' not found."
    except Exception as e:
        return f"Error running self-heal script: {str(e)}"
    
@tool
def get_container_environment_variables(container_name: str) -> str:
    """Get the configuration of a Docker container."""
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        env_vars = container.attrs['Config']['Env']
        return f"Environment variables for '{container_name}': {env_vars}"
    except docker.errors.NotFound:
        return f"Container '{container_name}' not found."
    except Exception as e:
        return f"Error fetching environment variables: {str(e)}"

def get_tools():
    """
    Returns a list of tools available for the agent
    """
    return [
        check_endpoint_health,
        get_container_status,
        get_recent_logs,
        check_resource_usage,
        send_slack_alert,
        run_self_heal_script
    ]