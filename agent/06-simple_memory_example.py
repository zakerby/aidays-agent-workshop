"""
Simple example demonstrating key memory concepts in smolagents.

This example shows:
1. How to access agent memory
2. How to use step callbacks
3. How to inject historical data
4. How to analyze memory patterns
"""

from smolagents import CodeAgent, LiteLLMModel, ActionStep, TaskStep
import time

def simple_memory_callback(memory_step: ActionStep, agent: CodeAgent) -> None:
    """
    Simple callback that adds timestamps and counts errors.
    This demonstrates how callbacks can modify memory dynamically.
    """
    if isinstance(memory_step, ActionStep):
        # Add timestamp to observations
        if memory_step.observations:
            timestamp = time.strftime("%H:%M:%S")
            memory_step.observations = f"[{timestamp}] {memory_step.observations}"
        
        # Count errors in recent history
        error_count = sum(1 for step in agent.memory.steps[-5:] 
                         if isinstance(step, ActionStep) and step.error is not None)
        
        if error_count >= 2:
            memory_step.observations = (memory_step.observations or "") + f"\n[WARNING] {error_count} errors in last 5 steps"

def demonstrate_basic_memory():
    """Demonstrate basic memory operations."""
    print("=== BASIC MEMORY DEMONSTRATION ===\n")
    
    # Create agent with memory callback
    model = LiteLLMModel(
        model_id="ollama_chat/llama3.2", 
        api_base="http://localhost:11434"
    )
    
    agent = CodeAgent(
        tools=[], 
        model=model, 
        verbosity_level=1,
        step_callbacks=[simple_memory_callback]  # Add our callback
    )
    
    print("1. Running agent with a simple task...")
    result = agent.run("Calculate 2 + 2 and then 3 * 4")
    
    print("\n2. Accessing agent memory:")
    
    # Access system prompt
    system_prompt = agent.memory.system_prompt.system_prompt
    print(f"System prompt length: {len(system_prompt)} characters")
    
    # Count different types of steps
    task_steps = []
    action_steps = []
    
    for step in agent.memory.steps:
        if isinstance(step, TaskStep):
            task_steps.append(step)
        elif isinstance(step, ActionStep):
            action_steps.append(step)
    
    print(f"Task steps: {len(task_steps)}")
    print(f"Action steps: {len(action_steps)}")
    
    # Show recent action steps with observations
    print("\n3. Recent action steps:")
    for i, step in enumerate(action_steps[-3:], 1):
        print(f"  Step {step.step_number}:")
        if step.observations:
            print(f"    Observations: {step.observations[:100]}...")
        if step.error:
            print(f"    Error: {step.error}")
        if step.code_action:
            print(f"    Code: {step.code_action[:50]}...")
    
    print("\n4. Converting memory to messages:")
    messages = agent.write_memory_to_messages()
    print(f"Memory converted to {len(messages)} LLM messages")
    
    print("\n5. Getting memory as dictionaries:")
    succinct_steps = agent.memory.get_succinct_steps()
    full_steps = agent.memory.get_full_steps()
    print(f"Succinct representation: {len(succinct_steps)} steps")
    print(f"Full representation: {len(full_steps)} steps")
    
    return agent

def demonstrate_memory_injection(agent: CodeAgent):
    """Demonstrate injecting historical data into memory."""
    print("\n=== MEMORY INJECTION DEMONSTRATION ===\n")
    
    # Inject a previous task
    previous_task = TaskStep(task="Previous calculation session")
    agent.memory.steps.insert(0, previous_task)  # Insert at beginning
    
    # Inject some historical action steps
    historical_actions = [
        ActionStep(
            step_number=0,
            observations="[HISTORICAL] Previous calculation: 5 + 5 = 10",
            timing=None
        ),
        ActionStep(
            step_number=0,
            observations="[HISTORICAL] Previous calculation failed due to syntax error",
            error="SyntaxError: invalid syntax",
            timing=None
        )
    ]
    
    # Insert historical steps
    for step in historical_actions:
        agent.memory.steps.insert(-1, step)  # Insert before last step
    
    print(f"Injected {len(historical_actions) + 1} historical steps")
    print(f"Total memory steps now: {len(agent.memory.steps)}")
    
    # Show how the agent can use this historical context
    print("\nRunning agent with historical context...")
    result = agent.run("Based on my previous calculations, what's a good next mathematical problem to solve?")
    
    return agent

def demonstrate_step_by_step_execution():
    """Demonstrate running agent step by step with memory control."""
    print("\n=== STEP-BY-STEP EXECUTION ===\n")
    
    model = LiteLLMModel(
        model_id="ollama_chat/llama3.2", 
        api_base="http://localhost:11434"
    )
    
    agent = CodeAgent(tools=[], model=model, verbosity_level=1)
    
    # Start with a task
    task = "Calculate the factorial of 5"
    agent.memory.steps.append(TaskStep(task=task))
    
    print(f"Starting task: {task}")
    
    final_answer = None
    step_number = 1
    max_steps = 5
    
    while final_answer is None and step_number <= max_steps:
        print(f"\n--- Step {step_number} ---")
        
        # Create action step
        memory_step = ActionStep(
            step_number=step_number,
            observations_images=[],
        )
        
        # Run one step
        try:
            final_answer = agent.step(memory_step)
            agent.memory.steps.append(memory_step)
            
            # Print step results
            print(f"Code executed: {memory_step.code_action}")
            if memory_step.observations:
                print(f"Observations: {memory_step.observations}")
            if memory_step.error:
                print(f"Error: {memory_step.error}")
                
        except Exception as e:
            print(f"Step failed: {e}")
            break
            
        step_number += 1
    
    print(f"\nFinal answer: {final_answer}")
    print(f"Total steps executed: {len(agent.memory.steps)}")
    
    return agent

def main():
    """Run all memory demonstrations."""
    print("SMOLAGENTS MEMORY EXAMPLES")
    print("=" * 50)
    
    try:
        # Basic memory operations
        agent1 = demonstrate_basic_memory()
        
        # Memory injection
        agent2 = demonstrate_memory_injection(agent1)
        
        # Step-by-step execution
        agent3 = demonstrate_step_by_step_execution()
        
        print("\n=== FINAL MEMORY REPLAY ===")
        print("Replaying the last agent's memory:")
        agent3.replay()
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure Ollama is running with the llama3.2 model")

if __name__ == "__main__":
    main()
