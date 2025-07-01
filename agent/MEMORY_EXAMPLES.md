# Smolagents Memory Usage Examples

This directory contains examples demonstrating how to use memory in smolagents effectively.

## Key Memory Concepts in Smolagents

### 1. Agent Memory Structure
Every agent has a `memory` object containing:
- **System Prompt**: The initial instructions given to the agent
- **Steps**: A list of all actions taken by the agent
  - `TaskStep`: Represents a new task given to the agent
  - `ActionStep`: Represents an action taken by the agent (tool call, code execution)
  - `PlanningStep`: Represents planning phases (when planning is enabled)

### 2. Memory Access
```python
# Access system prompt
system_prompt = agent.memory.system_prompt.system_prompt

# Access all steps
for step in agent.memory.steps:
    if isinstance(step, ActionStep):
        print(f"Step {step.step_number}: {step.observations}")

# Get memory as dictionaries
succinct_steps = agent.memory.get_succinct_steps()  # Without model input messages
full_steps = agent.memory.get_full_steps()          # With all details
```

### 3. Memory Callbacks
Use step callbacks to modify memory dynamically:
```python
def my_callback(memory_step: ActionStep, agent: CodeAgent) -> None:
    # Add timestamp to observations
    if memory_step.observations:
        timestamp = datetime.now().isoformat()
        memory_step.observations = f"[{timestamp}] {memory_step.observations}"

agent = CodeAgent(
    tools=tools,
    model=model,
    step_callbacks=[my_callback]  # Register callback
)
```

### 4. Memory Injection
Inject historical data or context:
```python
# Add previous task
previous_task = TaskStep(task="Previous monitoring session")
agent.memory.steps.append(previous_task)

# Add historical action
historical_step = ActionStep(
    step_number=0,
    observations="Historical data: System was down for 2 hours yesterday",
    timing=None
)
agent.memory.steps.append(historical_step)
```

### 5. Step-by-Step Execution
Control agent execution step by step:
```python
# Start with a task
agent.memory.steps.append(TaskStep(task="Monitor the system"))

final_answer = None
step_number = 1

while final_answer is None and step_number <= max_steps:
    memory_step = ActionStep(step_number=step_number, observations_images=[])
    final_answer = agent.step(memory_step)
    agent.memory.steps.append(memory_step)
    step_number += 1
```

## Examples

### 1. Simple Memory Example (`simple_memory_example.py`)
Basic demonstration of memory concepts:
```bash
python simple_memory_example.py
```

**Features:**
- Basic memory access
- Step callbacks
- Memory injection
- Step-by-step execution

### 2. Memory-Enhanced Monitoring Agent (`06-memory_example.py`)
Advanced example for monitoring applications with memory:
```bash
python 06-memory_example.py --demo_mode full
```

**Features:**
- Health check pattern analysis
- Historical monitoring data injection
- Memory-based decision making
- Step-by-step monitoring

**Demo modes:**
- `replay`: Show memory replay functionality
- `inject`: Demonstrate memory injection
- `step_by_step`: Show step-by-step execution
- `full`: Run all demonstrations

### 3. Integration with Your Existing Agent
To add memory capabilities to your existing `05-main.py`:

```python
# Add step callback for health tracking
def track_health_patterns(memory_step: ActionStep, agent) -> None:
    if memory_step.observations and "health" in memory_step.observations.lower():
        # Count recent failures
        failures = sum(1 for step in agent.memory.steps[-10:] 
                      if isinstance(step, ActionStep) and 
                      step.observations and "500" in step.observations)
        
        if failures >= 3:
            memory_step.observations += f"\n[ALERT] Pattern detected: {failures} failures in last 10 checks"

# Modify your create_agent function
def create_agent(llm_url: str, model: str) -> ToolCallingAgent:
    model = get_model(llm_url, model)
    agent = ToolCallingAgent(
        model=model, 
        tools=get_tools(),
        name="ai_monitoring_agent",
        description="An agent that monitors a web application and manages its health.",
        verbosity_level=2,
        step_callbacks=[track_health_patterns]  # Add memory callback
    )
    return agent
```

## Memory Best Practices

### 1. Use Callbacks for Dynamic Updates
- Add timestamps to observations
- Track patterns across steps
- Remove old images to save tokens
- Add contextual information

### 2. Inject Relevant Historical Data
- Previous monitoring sessions
- Known issues and resolutions
- System performance baselines
- Maintenance schedules

### 3. Analyze Memory for Patterns
```python
# Count specific types of events
error_count = sum(1 for step in agent.memory.steps 
                 if isinstance(step, ActionStep) and step.error is not None)

# Find patterns in observations
health_checks = [step for step in agent.memory.steps 
                if isinstance(step, ActionStep) and 
                step.observations and "health" in step.observations.lower()]
```

### 4. Use Step-by-Step for Long-Running Tasks
- Break down complex monitoring loops
- Save state between steps
- Handle interruptions gracefully
- Analyze memory at each step

### 5. Convert Memory to Messages for Analysis
```python
# Get memory as LLM-readable messages
messages = agent.write_memory_to_messages()

# Use for analysis or feeding to another agent
analysis_agent.run(f"Analyze this monitoring history: {messages}")
```

## Memory Storage and Persistence

### Current Limitations
- Memory is only stored in RAM during agent execution
- Memory is lost when the agent process ends

### Workarounds for Persistence
```python
import json

# Save memory to file
full_steps = agent.memory.get_full_steps()
with open("agent_memory.json", "w") as f:
    json.dump(full_steps, f, default=str)

# Load memory from file
with open("agent_memory.json", "r") as f:
    loaded_steps = json.load(f)
    # Convert back to memory steps and inject
```

## Troubleshooting

### Common Issues
1. **Memory growing too large**: Use callbacks to remove old images or truncate observations
2. **Step callbacks not working**: Ensure callback signature matches `(memory_step, agent)`
3. **Memory injection not affecting behavior**: Make sure injected steps are relevant and properly formatted

### Debug Memory
```python
# Print detailed memory information
agent.replay(detailed=True)  # Shows memory at each step

# Access raw memory data
print(f"Total steps: {len(agent.memory.steps)}")
for i, step in enumerate(agent.memory.steps):
    print(f"Step {i}: {type(step).__name__}")
```

## Running the Examples

1. Make sure Ollama is running with llama3.2:
```bash
docker exec ollama ollama run llama3.2
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run examples:
```bash
# Simple example
python simple_memory_example.py

# Full monitoring example
python 06-memory_example.py --demo_mode full

# Step-by-step only
python 06-memory_example.py --demo_mode step_by_step
```
