"""Base agent class and interfaces."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class TaskResult:
    """Result of a task execution by an agent."""
    
    success: bool
    output: Any
    tokens_used: int = 0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """Message passed between agents."""
    
    sender_id: str
    content: Any
    message_type: str = "default"
    metadata: Dict[str, Any] = field(default_factory=dict)


class Agent(ABC):
    """
    Abstract base class for all agent types.
    
    Based on the paper "Towards a Science of Scaling Agent Systems",
    this class defines the interface for agents that can execute tasks,
    communicate with other agents, and track their performance metrics.
    """
    
    def __init__(self, agent_id: str, capabilities: Optional[Dict[str, Any]] = None):
        """
        Initialize an agent.
        
        Args:
            agent_id: Unique identifier for this agent
            capabilities: Dictionary of agent capabilities (e.g., model type, token budget)
        """
        self.agent_id = agent_id
        self.capabilities = capabilities or {}
        self.tokens_used = 0
        self.tasks_completed = 0
        self.errors_count = 0
        self.message_history: List[Message] = []
    
    @abstractmethod
    def execute_task(self, task: Any, context: Optional[Dict[str, Any]] = None) -> TaskResult:
        """
        Execute a task and return the result.
        
        Args:
            task: The task to execute
            context: Optional context information
            
        Returns:
            TaskResult containing the execution outcome
        """
        pass
    
    def send_message(self, message: Message) -> None:
        """
        Send a message to other agents (stored in history).
        
        Args:
            message: Message to send
        """
        self.message_history.append(message)
    
    def receive_message(self, message: Message) -> None:
        """
        Receive a message from another agent.
        
        Args:
            message: Message received
        """
        self.message_history.append(message)
    
    def reset_metrics(self) -> None:
        """Reset all tracked metrics."""
        self.tokens_used = 0
        self.tasks_completed = 0
        self.errors_count = 0
        self.message_history = []
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current performance metrics.
        
        Returns:
            Dictionary of metrics
        """
        return {
            "agent_id": self.agent_id,
            "tokens_used": self.tokens_used,
            "tasks_completed": self.tasks_completed,
            "errors_count": self.errors_count,
            "messages_sent": len([m for m in self.message_history if m.sender_id == self.agent_id]),
            "messages_received": len([m for m in self.message_history if m.sender_id != self.agent_id]),
        }
