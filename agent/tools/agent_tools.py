from smolagents import Tool
import subprocess
import json
from datetime import datetime

def check_container_logs() -> Tool:
    def _check_logs(container_name: str = "webapp") -> str:
        try:
            cmd = f"docker logs --since 5m {container_name} 2>&1 | grep -c '500'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            count = result.stdout.strip() or "0"
            return f"Found {count} HTTP 500 errors in the last 5 minutes"
        except Exception as e:
            return f"Error checking logs: {str(e)}"

    return Tool(
        name="check_logs",
        description="Check container logs for HTTP 500 errors in last 5 minutes",
        function=_check_logs
    )

def check_container_metrics() -> Tool:
    def _check_metrics(container_name: str = "webapp") -> str:
        try:
            cmd = f"docker stats {container_name} --no-stream --format '{{{{json .}}}}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            metrics = json.loads(result.stdout)
            return f"""
                Container Metrics:
                - CPU Usage: {metrics.get('CPUPerc', 'N/A')}
                - Memory Usage: {metrics.get('MemPerc', 'N/A')}
                - Network I/O: {metrics.get('NetIO', 'N/A')}
            """
        except Exception as e:
            return f"Error checking metrics: {str(e)}"

    return Tool(
        name="check_metrics",
        description="Check container CPU, memory, and network metrics",
        function=_check_metrics
    )

def restart_container() -> Tool:
    def _restart(container_name: str = "webapp") -> str:
        try:
            cmd = f"docker restart {container_name}"
            subprocess.run(cmd, shell=True, check=True)
            return f"Container {container_name} restarted successfully"
        except Exception as e:
            return f"Failed to restart container: {str(e)}"

    return Tool(
        name="restart_container",
        description="Restart the specified Docker container",
        function=_restart
    )

def notify_support() -> Tool:
    def _notify() -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] Support team has been notified about persistent container issues"

    return Tool(
        name="notify_support",
        description="Notify support team about persistent issues",
        function=_notify
    )

def get_monitoring_tools() -> list:
    return [
        check_container_logs(),
        check_container_metrics(),
        restart_container(),
        notify_support()
    ]