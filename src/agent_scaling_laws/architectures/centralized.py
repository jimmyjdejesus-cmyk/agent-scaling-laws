"""Centralized multi-agent architecture implementation."""

from typing import Any, Dict, List, Optional, Tuple
from .base import Agent, TaskResult, Message


class CentralizedMultiAgent(Agent):
    """
    Centralized Multi-Agent Architecture.
    
    A single orchestrator manages all agents' behavior, maintains global state,
    and allocates tasks top-down.
    
    Characteristics (from paper):
    - Strong, predictable control
    - Error containment (4.4x amplification vs 17.2x for independent)
    - Excels at parallelizable tasks (80.9% improvement for financial tasks)
    - Scalability bottleneck at coordinator
    - Single point of failure risk
    """
    
    def __init__(
        self,
        agent_id: str = "centralized_system",
        num_agents: int = 3,
        capabilities: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize centralized multi-agent system.
        
        Args:
            agent_id: Unique identifier for this system
            num_agents: Number of worker agents
            capabilities: Dictionary of agent capabilities
        """
        super().__init__(agent_id, capabilities)
        self.num_agents = num_agents
        self.agents: List[Agent] = []
        self.global_state: Dict[str, Any] = {}
        
        # Create worker agents
        from .single_agent import SingleAgent
        for i in range(num_agents):
            agent = SingleAgent(
                agent_id=f"{agent_id}_worker_{i}",
                capabilities=capabilities
            )
            self.agents.append(agent)
    
    def _decompose_task(self, task: Any, context: Optional[Dict[str, Any]]) -> List[Tuple[Agent, Any]]:
        """
        Decompose task into subtasks and assign to agents.
        
        Args:
            task: The task to decompose
            context: Optional context information
            
        Returns:
            List of (agent, subtask) pairs
        """
        # Simple decomposition: distribute task to all agents
        # In a real implementation, this would intelligently partition the task
        assignments = []
        
        if isinstance(task, (list, tuple)):
            # Distribute items across agents
            for i, item in enumerate(task):
                agent_idx = i % self.num_agents
                assignments.append((self.agents[agent_idx], item))
        else:
            # Single task - assign to first available agent
            assignments.append((self.agents[0], task))
        
        return assignments
    
    def _coordinate_execution(
        self,
        assignments: List[Tuple[Agent, Any]],
        context: Optional[Dict[str, Any]]
    ) -> List[TaskResult]:
        """
        Coordinate execution of subtasks by agents.
        
        Args:
            assignments: List of (agent, subtask) pairs
            context: Optional context information
            
        Returns:
            List of TaskResults from agents
        """
        results = []
        
        for agent, subtask in assignments:
            # Orchestrator coordinates each agent
            # Share global state through context
            enriched_context = {**(context or {}), "global_state": self.global_state}
            
            result = agent.execute_task(subtask, enriched_context)
            results.append(result)
            
            # Update global state based on result
            if result.success:
                self.global_state[f"result_{agent.agent_id}"] = result.output
            
            # Coordinator overhead (token cost)
            coord_tokens = self.capabilities.get("coordination_tokens_per_task", 10)
            self.tokens_used += coord_tokens
        
        return results
    
    def _aggregate_results(self, results: List[TaskResult]) -> TaskResult:
        """
        Aggregate results from multiple agents.
        
        Args:
            results: List of TaskResults from agents
            
        Returns:
            Aggregated TaskResult
        """
        successful_results = [r for r in results if r.success]
        total_tokens = sum(r.tokens_used for r in results) + self.tokens_used
        
        if successful_results:
            # Aggregate outputs
            outputs = [r.output for r in successful_results]
            
            # Simple aggregation - could be more sophisticated
            if len(outputs) == 1:
                final_output = outputs[0]
            else:
                final_output = outputs
            
            self.tasks_completed += len(successful_results)
            
            return TaskResult(
                success=True,
                output=final_output,
                tokens_used=total_tokens,
                metadata={
                    "architecture": "centralized",
                    "num_agents": self.num_agents,
                    "successful_subtasks": len(successful_results),
                    "failed_subtasks": len(results) - len(successful_results),
                    "coordination_overhead": self.tokens_used,
                }
            )
        else:
            self.errors_count += len(results)
            return TaskResult(
                success=False,
                output=None,
                tokens_used=total_tokens,
                error="All subtasks failed",
                metadata={
                    "architecture": "centralized",
                    "num_agents": self.num_agents,
                }
            )
    
    def execute_task(self, task: Any, context: Optional[Dict[str, Any]] = None) -> TaskResult:
        """
        Execute task with centralized coordination.
        
        The coordinator decomposes the task, assigns subtasks to agents,
        coordinates execution, and aggregates results.
        
        Args:
            task: The task to execute
            context: Optional context information
            
        Returns:
            TaskResult containing aggregated results
        """
        # Reset global state for new task
        self.global_state = {}
        
        # Decompose task into subtasks
        assignments = self._decompose_task(task, context)
        
        # Coordinate execution
        results = self._coordinate_execution(assignments, context)
        
        # Aggregate and return results
        return self._aggregate_results(results)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics from coordinator and all agents."""
        base_metrics = super().get_metrics()
        
        # Aggregate agent metrics
        agent_metrics = [agent.get_metrics() for agent in self.agents]
        base_metrics["agents"] = agent_metrics
        base_metrics["total_agent_tokens"] = sum(a["tokens_used"] for a in agent_metrics)
        base_metrics["coordination_overhead"] = self.tokens_used
        
        return base_metrics
