from smolagents import tool
import docker

@tool
def check_endpoint_health(url: str = "http://localhost:5000") -> str:
    """
    Check the health status of a web application endpoint.
    
    Args:
        url (str): The URL of the web application endpoint to check.
        
    Returns:
        str: The health status of the endpoint.
    """
    import requests
    try:
        response = requests.get(f"{url}/health_check")
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
def restart_container(container_name: str) -> str: 
    """
    Restart a Docker container to self-heal it.
    Args:
        container_name (str): The name of the Docker container to fetch logs from.
    Returns:
        str: Confirmation of the restart action or an error message.
    """
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        container.restart()
        return f"Self-heal script '{container_name}' executed successfully."
    except docker.errors.NotFound:
        return f"Container '{container_name}' not found."
    except Exception as e:
        return f"Error running self-heal script: {str(e)}"
    
@tool
def get_container_environment_variables(container_name: str) -> str:
    """
    Get the configuration of a Docker container.
    Args:
        container_name (str): The name of the Docker container to fetch environment variables from.
    Returns:
        str: The environment variables of the container or an error message.
    """
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
        get_recent_logs,
        check_resource_usage,
        send_slack_alert,
        restart_container
    ]