from smolagents import CodeAgent, LiteLLMModel, ToolCallingAgent, ActionStep, TaskStep
import argparse
from datetime import datetime
from tools.tools import get_tools

def get_model(llm_url: str, model_name: str = "ollama_chat/llama3.2") -> LiteLLMModel:
    return LiteLLMModel(
        model_id=model_name,
        api_base=llm_url,
        max_tokens=1024,
        temperature=0.1,
        top_p=0.95,
        top_k=40,
        stop=["\n\n"],
    )

def create_memory_enhanced_agent(llm_url: str, model: str) -> ToolCallingAgent:
    """
    Create and return a ToolCallingAgent with memory-enhanced monitoring capabilities.
    """
    model = get_model(llm_url, model)
    
    # Create agent with step callbacks for memory management
    agent = ToolCallingAgent(
        model=model, 
        tools=get_tools(),
        name="memory_monitoring_agent",
        description="An agent that monitors web applications with memory of past health checks.",
        verbosity_level=2,
        step_callbacks=[log_health_check_history]  # Custom callback to track health status
    )
    
    return agent

def log_health_check_history(memory_step: ActionStep, agent: ToolCallingAgent) -> None:
    """
    Custom callback to track health check history and analyze patterns.
    This function is called after each step to update memory with health insights.
    """
    if isinstance(memory_step, ActionStep) and memory_step.observations:
        # Track health check results in agent memory
        timestamp = datetime.now().isoformat()
        
        # Add timestamp and context to observations
        enhanced_observation = f"[{timestamp}] {memory_step.observations}"
        memory_step.observations = enhanced_observation
        
        # Count recent health check failures for pattern analysis
        failure_count = 0
        for step in agent.memory.steps[-10:]:  # Look at last 10 steps
            if isinstance(step, ActionStep) and step.observations:
                if "status code" in step.observations and "200" not in step.observations:
                    failure_count += 1
                elif "Error checking endpoint" in step.observations:
                    failure_count += 1
        
        # Add pattern analysis to current step
        if failure_count >= 3:
            memory_step.observations += f"\n[PATTERN DETECTED] {failure_count} failures in last 10 checks - potential service degradation"

def demonstrate_memory_access(agent: ToolCallingAgent):
    """
    Demonstrate how to access and analyze agent memory.
    """
    print("\n=== AGENT MEMORY ANALYSIS ===")
    
    # Access system prompt
    system_prompt_step = agent.memory.system_prompt
    print("System prompt:", system_prompt_step.system_prompt[:100] + "...")
    
    # Analyze recent steps
    print(f"\nTotal steps in memory: {len(agent.memory.steps)}")
    
    # Find health check related steps
    health_checks = []
    errors = []
    
    for step in agent.memory.steps:
        if isinstance(step, ActionStep):
            if step.error is not None:
                errors.append(f"Step {step.step_number}: {step.error}")
            elif step.observations and "Endpoint" in step.observations:
                health_checks.append(f"Step {step.step_number}: {step.observations}")
    
    print(f"\nHealth checks performed: {len(health_checks)}")
    for check in health_checks[-3:]:  # Show last 3
        print(f"  {check}")
    
    print(f"\nErrors encountered: {len(errors)}")
    for error in errors[-2:]:  # Show last 2 errors
        print(f"  {error}")
    
    # Get full step details for analysis
    full_steps = agent.memory.get_full_steps()
    print(f"\nFull memory contains {len(full_steps)} detailed steps")

def inject_historical_memory(agent: ToolCallingAgent):
    """
    Demonstrate how to inject historical monitoring data into agent memory.
    This simulates previous monitoring sessions.
    """
    print("\n=== INJECTING HISTORICAL MEMORY ===")
    
    # Simulate previous monitoring tasks
    previous_task = TaskStep(task="Previous monitoring session: Monitor python-app health")
    agent.memory.steps.append(previous_task)
    
    # Simulate some historical health checks
    historical_checks = [
        "Endpoint http://localhost:5000 is healthy.",
        "Endpoint http://localhost:5000 returned status code 500.",
        "Container 'python-app' restarted successfully.",
        "Endpoint http://localhost:5000 is healthy."
    ]
    
    for i, observation in enumerate(historical_checks, 1):
        historical_step = ActionStep(
            step_number=i,
            observations=f"[HISTORICAL] {observation}",
            timing=None  # We don't have timing data for historical steps
        )
        agent.memory.steps.append(historical_step)
    
    print(f"Injected {len(historical_checks)} historical monitoring steps")

def run_step_by_step_monitoring(agent: ToolCallingAgent, webapp_url: str):
    """
    Demonstrate step-by-step agent execution with memory control.
    """
    print("\n=== STEP-BY-STEP MONITORING ===")
    
    # Start new monitoring task
    task = f"Check the health of {webapp_url} and analyze patterns from memory"
    agent.memory.steps.append(TaskStep(task=task, task_images=[]))
    
    final_answer = None
    step_number = len(agent.memory.steps) + 1
    max_steps = 3
    
    while final_answer is None and step_number <= max_steps:
        memory_step = ActionStep(
            step_number=step_number,
            observations_images=[],
        )
        
        # Run one step
        final_answer = agent.step(memory_step)
        agent.memory.steps.append(memory_step)
        
        # Analyze memory after each step
        print(f"\nAfter step {step_number}:")
        if memory_step.observations:
            print(f"  Observations: {memory_step.observations}")
        if memory_step.error:
            print(f"  Error: {memory_step.error}")
        
        step_number += 1
    
    print(f"\nStep-by-step monitoring completed. Final answer: {final_answer}")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Memory-Enhanced AI Monitoring Agent')
    parser.add_argument('--llm_url', default='http://localhost:11434', help='LLM base URL')
    parser.add_argument('--model', default='gemma:2b', help='LLM model name')
    parser.add_argument('--webapp_url', default='http://localhost:5000', help='URL of the web application to monitor')
    parser.add_argument('--demo_mode', choices=['replay', 'inject', 'step_by_step', 'full'], 
                       default='full', help='Demo mode to run')
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    print(f"Starting memory-enhanced monitoring agent with model: {args.model}")
    
    # Create agent with memory capabilities
    agent = create_memory_enhanced_agent(args.llm_url, args.model)
    
    if args.demo_mode in ['inject', 'full']:
        # Demonstrate memory injection
        inject_historical_memory(agent)
    
    if args.demo_mode in ['step_by_step', 'full']:
        # Demonstrate step-by-step execution
        run_step_by_step_monitoring(agent, args.webapp_url)
    else:
        # Run normal monitoring with memory
        agent.run(f"""
        You are a memory-enhanced monitoring agent. Check the health of {args.webapp_url}.
        
        Use your memory to:
        1. Analyze patterns from previous health checks
        2. Look for recurring issues
        3. Make informed decisions based on historical data
        
        After checking health, analyze your memory for patterns and provide insights.
        """)
    
    if args.demo_mode in ['replay', 'full']:
        # Demonstrate memory analysis and replay
        demonstrate_memory_access(agent)
        
        print("\n=== REPLAYING AGENT MEMORY ===")
        agent.replay()  # Show detailed replay of all steps
    
    # Show how to convert memory to messages for LLM
    print("\n=== MEMORY AS LLM MESSAGES ===")
    messages = agent.write_memory_to_messages()
    print(f"Memory converted to {len(messages)} LLM messages")
    for i, message in enumerate(messages[:3]):  # Show first 3 messages
        print(f"Message {i+1} ({message.role}): {str(message.content)[:100]}...")

if __name__ == "__main__":
    main()
