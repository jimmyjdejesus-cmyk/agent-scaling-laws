"""Single agent architecture implementation."""

from typing import Any, Dict, Optional
from .base import Agent, TaskResult


class SingleAgent(Agent):
    """
    Single Agent Architecture.
    
    One agent independently reasons, plans, and acts on tasks.
    
    Characteristics (from paper):
    - Simple to design and maintain
    - Lower overhead (no coordination needed)
    - Limited scalability for complex tasks
    - Best for well-defined tasks with constrained scope
    """
    
    def __init__(self, agent_id: str = "single_agent", capabilities: Optional[Dict[str, Any]] = None):
        """
        Initialize a single agent.
        
        Args:
            agent_id: Unique identifier for this agent
            capabilities: Dictionary of agent capabilities
        """
        super().__init__(agent_id, capabilities)
    
    def execute_task(self, task: Any, context: Optional[Dict[str, Any]] = None) -> TaskResult:
        """
        Execute a task independently.
        
        Args:
            task: The task to execute (can be callable or data)
            context: Optional context information
            
        Returns:
            TaskResult containing the execution outcome
        """
        try:
            # Simulate task execution
            if callable(task):
                result = task(context or {})
            else:
                result = task
            
            # Track tokens (simplified - in real implementation would come from LLM)
            tokens = self.capabilities.get("tokens_per_task", 100)
            self.tokens_used += tokens
            self.tasks_completed += 1
            
            return TaskResult(
                success=True,
                output=result,
                tokens_used=tokens,
                metadata={
                    "architecture": "single",
                    "agent_id": self.agent_id,
                }
            )
        except Exception as e:
            self.errors_count += 1
            return TaskResult(
                success=False,
                output=None,
                error=str(e),
                metadata={
                    "architecture": "single",
                    "agent_id": self.agent_id,
                }
            )
