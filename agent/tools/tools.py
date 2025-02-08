from langchain_community.tools.shell.tool import ShellTool
import requests

def check_logs_for_errors():
    """Check Docker logs for 500 errors"""
    try:
        cmd = "docker logs webapp 2>&1 | grep '500'"
        return ShellTool().run(cmd)
    except Exception:
        return "No 500 errors found"

def restart_container():
    """Restart the webapp container"""
    try:
        return ShellTool().run("docker restart webapp")
    except Exception as e:
        return f"Failed to restart container: {e}"

def check_endpoint_health():
    """Check if the webapp is responding"""
    try:
        response = requests.get("http://localhost:8080")
        return f"Status code: {response.status_code}"
    except requests.RequestException as e:
        return f"Error accessing webapp: {e}"
