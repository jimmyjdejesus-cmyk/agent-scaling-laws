"""Hybrid multi-agent architecture implementation."""

from typing import Any, Dict, List, Optional
from .base import Agent, TaskResult, Message


class HybridMultiAgent(Agent):
    """
    Hybrid Multi-Agent Architecture.
    
    Combines centralized strategic oversight with decentralized tactical execution.
    High-level manager sets goals while semi-autonomous teams coordinate amongst themselves.
    
    Characteristics (from paper):
    - Balances control with flexibility
    - Dynamic adaptation based on task needs
    - Mixes hierarchy with peer collaboration
    - Optimal scalability and resiliency
    - Context-dependent performance
    """
    
    def __init__(
        self,
        agent_id: str = "hybrid_system",
        num_agents: int = 6,
        team_size: int = 2,
        capabilities: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize hybrid multi-agent system.
        
        Args:
            agent_id: Unique identifier for this system
            num_agents: Total number of worker agents
            team_size: Size of each decentralized team
            capabilities: Dictionary of agent capabilities
        """
        super().__init__(agent_id, capabilities)
        self.num_agents = num_agents
        self.team_size = team_size
        self.num_teams = max(1, num_agents // team_size)
        
        # Create teams of agents
        self.teams: List[List[Agent]] = []
        self.global_state: Dict[str, Any] = {}
        self.team_messages: Dict[int, List[Message]] = {}
        
        from .single_agent import SingleAgent
        for team_idx in range(self.num_teams):
            team = []
            for agent_idx in range(team_size):
                agent = SingleAgent(
                    agent_id=f"{agent_id}_team{team_idx}_agent{agent_idx}",
                    capabilities=capabilities
                )
                team.append(agent)
            self.teams.append(team)
            self.team_messages[team_idx] = []
    
    def _strategic_decomposition(
        self,
        task: Any,
        context: Optional[Dict[str, Any]]
    ) -> List[Any]:
        """
        Centralized strategic decomposition of task into team-level tasks.
        
        Args:
            task: The task to decompose
            context: Optional context information
            
        Returns:
            List of team-level tasks
        """
        # Coordination overhead for strategic planning
        strategy_tokens = self.capabilities.get("strategy_tokens", 20)
        self.tokens_used += strategy_tokens
        
        # Simple decomposition: distribute across teams
        if isinstance(task, (list, tuple)):
            # Chunk task for teams
            team_tasks = []
            chunk_size = max(1, len(task) // self.num_teams)
            for i in range(self.num_teams):
                start = i * chunk_size
                end = start + chunk_size if i < self.num_teams - 1 else len(task)
                team_tasks.append(task[start:end])
            return team_tasks
        else:
            # Single task - assign to first team
            return [task] + [None] * (self.num_teams - 1)
    
    def _team_coordination(
        self,
        team: List[Agent],
        team_idx: int,
        team_task: Any,
        context: Optional[Dict[str, Any]]
    ) -> TaskResult:
        """
        Decentralized coordination within a team.
        
        Args:
            team: List of agents in the team
            team_idx: Index of the team
            team_task: Task for this team
            context: Optional context information
            
        Returns:
            Team's aggregated TaskResult
        """
        if team_task is None:
            return TaskResult(
                success=True,
                output=None,
                tokens_used=0,
                metadata={"team_idx": team_idx, "status": "no_task"}
            )
        
        team_results = []
        
        # Team members collaborate through peer communication
        for agent in team:
            # Agent sees team context and messages
            team_context = {
                **(context or {}),
                "team_idx": team_idx,
                "team_messages": self.team_messages[team_idx],
                "global_state": self.global_state,
            }
            
            result = agent.execute_task(team_task, team_context)
            team_results.append(result)
            
            # Share result within team
            if result.success:
                message = Message(
                    sender_id=agent.agent_id,
                    content=result.output,
                    message_type="team_result",
                    metadata={"team_idx": team_idx}
                )
                self.team_messages[team_idx].append(message)
                
                # Intra-team communication overhead
                comm_tokens = self.capabilities.get("team_comm_tokens", 3)
                self.tokens_used += comm_tokens
        
        # Team consensus
        successful = [r for r in team_results if r.success]
        if successful:
            total_tokens = sum(r.tokens_used for r in team_results)
            return TaskResult(
                success=True,
                output=successful[-1].output,  # Use latest success
                tokens_used=total_tokens,
                metadata={
                    "team_idx": team_idx,
                    "team_size": len(team),
                    "successful_members": len(successful),
                }
            )
        else:
            return TaskResult(
                success=False,
                output=None,
                error="Team failed to complete task",
                metadata={"team_idx": team_idx}
            )
    
    def _aggregate_team_results(self, team_results: List[TaskResult]) -> TaskResult:
        """
        Centralized aggregation of team results.
        
        Args:
            team_results: Results from all teams
            
        Returns:
            Final aggregated TaskResult
        """
        # Coordination overhead for aggregation
        agg_tokens = self.capabilities.get("aggregation_tokens", 15)
        self.tokens_used += agg_tokens
        
        successful_teams = [r for r in team_results if r.success and r.output is not None]
        total_tokens = sum(r.tokens_used for r in team_results) + self.tokens_used
        
        if successful_teams:
            # Aggregate team outputs
            outputs = [r.output for r in successful_teams]
            
            if len(outputs) == 1:
                final_output = outputs[0]
            else:
                # Combine outputs (could be more sophisticated)
                final_output = outputs
            
            self.tasks_completed += len(successful_teams)
            
            return TaskResult(
                success=True,
                output=final_output,
                tokens_used=total_tokens,
                metadata={
                    "architecture": "hybrid",
                    "num_teams": self.num_teams,
                    "team_size": self.team_size,
                    "successful_teams": len(successful_teams),
                    "failed_teams": len(team_results) - len(successful_teams),
                    "coordination_overhead": self.tokens_used,
                }
            )
        else:
            self.errors_count += len(team_results)
            return TaskResult(
                success=False,
                output=None,
                tokens_used=total_tokens,
                error="All teams failed",
                metadata={
                    "architecture": "hybrid",
                    "num_teams": self.num_teams,
                }
            )
    
    def execute_task(self, task: Any, context: Optional[Dict[str, Any]] = None) -> TaskResult:
        """
        Execute task with hybrid coordination.
        
        Centralized strategic planning decomposes task into team assignments.
        Teams execute with decentralized peer coordination.
        Results are centrally aggregated.
        
        Args:
            task: The task to execute
            context: Optional context information
            
        Returns:
            TaskResult containing final aggregated result
        """
        # Reset state
        self.global_state = {}
        self.team_messages = {i: [] for i in range(self.num_teams)}
        
        # Strategic decomposition (centralized)
        team_tasks = self._strategic_decomposition(task, context)
        
        # Team execution (decentralized within teams)
        team_results = []
        for team_idx, (team, team_task) in enumerate(zip(self.teams, team_tasks)):
            result = self._team_coordination(team, team_idx, team_task, context)
            team_results.append(result)
            
            # Update global state
            if result.success:
                self.global_state[f"team_{team_idx}_result"] = result.output
        
        # Aggregate results (centralized)
        return self._aggregate_team_results(team_results)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics from all teams and agents."""
        base_metrics = super().get_metrics()
        
        # Aggregate agent metrics by team
        all_agents = [agent for team in self.teams for agent in team]
        agent_metrics = [agent.get_metrics() for agent in all_agents]
        
        base_metrics["teams"] = [
            {
                "team_idx": i,
                "agents": [agent.get_metrics() for agent in team]
            }
            for i, team in enumerate(self.teams)
        ]
        base_metrics["total_agent_tokens"] = sum(a["tokens_used"] for a in agent_metrics)
        base_metrics["coordination_overhead"] = self.tokens_used
        
        return base_metrics
