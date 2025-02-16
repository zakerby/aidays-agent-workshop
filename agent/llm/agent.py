from typing import Optional, Dict, Annotated, TypedDict
from typing_extensions import Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.prebuilt import ToolExecutor
from langgraph.graph import Graph, StateGraph
from operator import itemgetter
from langchain import hub
from langchain_core.prompts import PromptTemplate
from llm.llm import get_llm
from tools.tools import get_tools

# Define state structure
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], "Messages in conversation"]
    next: str  # Next node to run
    health_status: str  # Current health status
    logs: str  # Container logs if checked
    actions_taken: list[str]  # List of actions taken



MONITORING_PROMPT = PromptTemplate.from_template(
    """You are a system monitoring agent responsible for maintaining a web application's health.

    When monitoring, always follow these steps in order:
    1. Check the application's health status first
    2. If unhealthy or unreachable, check the logs for errors
    3. If errors are found or the app is down, restart the container
    4. Verify the application is healthy after any actions
    
    Current task: {input}
    
    Think through this step-by-step:
    1) First, what is the current state of the system?
    2) What actions, if any, need to be taken?
    3) How can we verify the system is healthy?
    """
)


MONITORING_PROMPT = PromptTemplate.from_template(
    """You are a system monitoring agent responsible for maintaining a web application's health.

    When monitoring, always follow these steps in order:
    1. Check the application's health status first
    2. If unhealthy or unreachable, check the logs for errors
    3. If errors are found or the app is down, restart the container
    4. Verify the application is healthy after any actions
    
    Current task: {input}
    
    Think through this step-by-step:
    1) First, what is the current state of the system?
    2) What actions, if any, need to be taken?
    3) How can we verify the system is healthy?

    Available tools: {tools}
    """
)

def create_agent(ollama_url: str, model_name: str) -> Optional[Graph]:
    try:
        # Initialize the LLM
        llm = get_llm(ollama_url, model_name)
        tools = get_tools()
        
        # Create tool executor
        tool_executor = ToolExecutor(tools)

        # Define agent nodes
        def check_health(state: AgentState) -> AgentState:
            """Check the health status of the application"""
            for tool in tools:
                if tool.name == "check_health":
                    result = tool_executor.invoke({"tool": "check_health"})
                    state["health_status"] = result
                    state["actions_taken"].append("health_check")
                    state["next"] = "analyze_status"
            return state

        def analyze_status(state: AgentState) -> AgentState:
            """Analyze health status and decide next action"""
            if "error" in state["health_status"].lower() or "500" in state["health_status"]:
                state["next"] = "check_logs"
            else:
                state["next"] = "end"
            return state

        def check_logs(state: AgentState) -> AgentState:
            """Check container logs if health check failed"""
            for tool in tools:
                if tool.name == "get_logs":
                    state["logs"] = tool_executor.invoke({"tool": "get_logs"})
                    state["actions_taken"].append("logs_checked")
                    state["next"] = "handle_issues"
            return state

        def handle_issues(state: AgentState) -> AgentState:
            """Handle any detected issues"""
            if state["logs"] and ("error" in state["logs"].lower() or "exception" in state["logs"].lower()):
                for tool in tools:
                    if tool.name == "restart_container":
                        tool_executor.invoke({"tool": "restart_container"})
                        state["actions_taken"].append("container_restarted")
            state["next"] = "verify_health"
            return state

        def verify_health(state: AgentState) -> AgentState:
            """Verify health after taking actions"""
            for tool in tools:
                if tool.name == "check_health":
                    state["health_status"] = tool_executor.invoke({"tool": "check_health"})
                    state["actions_taken"].append("health_verified")
            state["next"] = "end"
            return state

        # Create workflow graph
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("check_health", check_health)
        workflow.add_node("analyze_status", analyze_status)
        workflow.add_node("check_logs", check_logs)
        workflow.add_node("handle_issues", handle_issues)
        workflow.add_node("verify_health", verify_health)
        workflow.add_node("end", lambda state: state)

        # Add edges
        workflow.set_entry_point("check_health")
        workflow.add_edge("check_health", "analyze_status")
        workflow.add_edge("analyze_status", "check_logs")
        workflow.add_edge("analyze_status", "end")
        workflow.add_edge("check_logs", "handle_issues")
        workflow.add_edge("handle_issues", "verify_health")
        workflow.add_edge("verify_health", "end")

        # Compile workflow
        app = workflow.compile()
        
        return app

    except Exception as e:
        print(f"Error creating agent: {e}")
        return None