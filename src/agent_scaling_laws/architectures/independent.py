"""Independent multi-agent architecture implementation."""

from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base import Agent, TaskResult, Message


class IndependentMultiAgent(Agent):
    """
    Independent Multi-Agent Architecture.
    
    Multiple agents operate separately, each with its own goal and context.
    
    Characteristics (from paper):
    - Minimal coordination, mostly parallel execution
    - High risk of error amplification (17.2x in paper)
    - Lack of shared state or strategy
    - Potential inconsistency and redundancy
    - Use case: Parallel processing where independence is feasible
    """
    
    def __init__(
        self,
        agent_id: str = "independent_system",
        num_agents: int = 3,
        capabilities: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize independent multi-agent system.
        
        Args:
            agent_id: Unique identifier for this system
            num_agents: Number of independent agents
            capabilities: Dictionary of agent capabilities
        """
        super().__init__(agent_id, capabilities)
        self.num_agents = num_agents
        self.agents: List[Agent] = []
        
        # Create independent agents
        from .single_agent import SingleAgent
        for i in range(num_agents):
            agent = SingleAgent(
                agent_id=f"{agent_id}_agent_{i}",
                capabilities=capabilities
            )
            self.agents.append(agent)
    
    def execute_task(self, task: Any, context: Optional[Dict[str, Any]] = None) -> TaskResult:
        """
        Execute task with independent agents in parallel.
        
        Each agent works independently without coordination.
        
        Args:
            task: The task to execute
            context: Optional context information
            
        Returns:
            TaskResult containing aggregated results
        """
        results = []
        total_tokens = 0
        errors = []
        
        # Execute tasks in parallel
        with ThreadPoolExecutor(max_workers=self.num_agents) as executor:
            futures = {
                executor.submit(agent.execute_task, task, context): agent
                for agent in self.agents
            }
            
            for future in as_completed(futures):
                agent = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    total_tokens += result.tokens_used
                    
                    if not result.success:
                        errors.append(result.error)
                        self.errors_count += 1
                    else:
                        self.tasks_completed += 1
                        
                except Exception as e:
                    self.errors_count += 1
                    errors.append(str(e))
        
        self.tokens_used += total_tokens
        
        # Aggregate results (simple majority or first success)
        successful_results = [r for r in results if r.success]
        
        if successful_results:
            # Use first successful result (could be improved with voting)
            best_result = successful_results[0]
            return TaskResult(
                success=True,
                output=best_result.output,
                tokens_used=total_tokens,
                metadata={
                    "architecture": "independent",
                    "num_agents": self.num_agents,
                    "successful_agents": len(successful_results),
                    "failed_agents": len(results) - len(successful_results),
                }
            )
        else:
            return TaskResult(
                success=False,
                output=None,
                tokens_used=total_tokens,
                error=f"All agents failed. Errors: {errors}",
                metadata={
                    "architecture": "independent",
                    "num_agents": self.num_agents,
                }
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics from all agents."""
        base_metrics = super().get_metrics()
        
        # Aggregate agent metrics
        agent_metrics = [agent.get_metrics() for agent in self.agents]
        base_metrics["agents"] = agent_metrics
        base_metrics["total_agent_tokens"] = sum(a["tokens_used"] for a in agent_metrics)
        
        return base_metrics
