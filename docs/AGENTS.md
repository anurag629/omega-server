# Agent System

Omega Server uses a modular agent system to handle AI, script execution, Docker management, and dependency resolution. This design allows for easy extension and robust error handling.

---

## 1. Overview

Agents are Python classes that encapsulate a specific responsibility in the workflow:
- **AIScriptGenerationAgent**: Generates Manim scripts from prompts using AI providers.
- **ManimExecutionAgent**: Executes scripts in Docker, manages retries, and error handling.
- **DockerAgent**: Manages Docker containers for safe, isolated execution.
- **DependencyAgent**: Installs missing Python dependencies as needed.
- **AIScriptDebuggingAgent**: Uses AI to fix scripts that fail to execute.

---

## 2. Main Agents

### AIScriptGenerationAgent
- **Location**: `agents/agents/ai_agent.py`
- **Purpose**: Converts user prompts into Manim scripts using Gemini or Azure OpenAI.
- **Extending**: Add new providers by implementing new methods and updating provider selection logic.

### ManimExecutionAgent
- **Location**: `agents/agents/execution_agent.py`
- **Purpose**: Runs scripts in Docker, tracks execution, handles errors, and can invoke AI debugging.
- **Features**: Retry logic, dependency fixing, and output management.

### DockerAgent
- **Location**: `agents/agents/docker_agent.py`
- **Purpose**: Starts, stops, and checks status of Docker containers. Handles file transfer and command execution inside containers.

### DependencyAgent
- **Location**: `agents/agents/dependency_agent.py`
- **Purpose**: Installs missing Python packages required by scripts, based on error analysis.

### AIScriptDebuggingAgent
- **Location**: `agents/agents/ai_agent.py`
- **Purpose**: Uses AI to analyze and fix scripts that fail to execute, based on error messages.

---

## 3. Adding a New Agent

1. **Create a new Python class** in `agents/agents/` (e.g., `my_agent.py`).
2. **Inherit from `BaseAgent`** for logging and shared utilities.
3. **Implement your logic** (e.g., new AI provider, new execution strategy).
4. **Integrate** by updating viewsets or other agents to use your new agent as needed.

---

## 4. Example: Adding a New AI Provider

1. Add a method to `AIScriptGenerationAgent` (e.g., `_generate_with_newai`).
2. Update the provider selection logic in `generate()`.
3. Add provider configuration to the database and settings.

---

## 5. Best Practices
- Keep each agent focused on a single responsibility.
- Use logging for all major actions and errors.
- Handle exceptions gracefully and return structured results.

---

For more details, see the source code in `agents/agents/`. 