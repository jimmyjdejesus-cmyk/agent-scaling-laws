"""Decentralized multi-agent architecture implementation."""

from typing import Any, Dict, List, Optional
from .base import Agent, TaskResult, Message


class DecentralizedMultiAgent(Agent):
    """
    Decentralized Multi-Agent Architecture.
    
    Agents make decisions autonomously, communicating peer-to-peer.
    No single point of control.
    
    Characteristics (from paper):
    - Emergent, distributed control
    - Each agent adapts based on local information
    - Robustness and scalability
    - Suitable for dynamic tasks (9.2% improvement for web navigation)
    - Challenges: consistency, global coordination
    """
    
    def __init__(
        self,
        agent_id: str = "decentralized_system",
        num_agents: int = 3,
        capabilities: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize decentralized multi-agent system.
        
        Args:
            agent_id: Unique identifier for this system
            num_agents: Number of peer agents
            capabilities: Dictionary of agent capabilities
        """
        super().__init__(agent_id, capabilities)
        self.num_agents = num_agents
        self.agents: List[Agent] = []
        self.shared_messages: List[Message] = []
        
        # Create peer agents
        from .single_agent import SingleAgent
        for i in range(num_agents):
            agent = SingleAgent(
                agent_id=f"{agent_id}_peer_{i}",
                capabilities=capabilities
            )
            self.agents.append(agent)
    
    def _broadcast_message(self, sender: Agent, message: Message) -> None:
        """
        Broadcast message from one agent to all others.
        
        Args:
            sender: Agent sending the message
            message: Message to broadcast
        """
        self.shared_messages.append(message)
        
        # Communication overhead
        comm_tokens = self.capabilities.get("communication_tokens_per_message", 5)
        self.tokens_used += comm_tokens * (self.num_agents - 1)
        
        for agent in self.agents:
            if agent.agent_id != sender.agent_id:
                agent.receive_message(message)
    
    def _peer_to_peer_coordination(
        self,
        task: Any,
        context: Optional[Dict[str, Any]]
    ) -> List[TaskResult]:
        """
        Execute task with peer-to-peer coordination.
        
        Agents communicate and adapt based on peer information.
        
        Args:
            task: The task to execute
            context: Optional context information
            
        Returns:
            List of TaskResults from agents
        """
        results = []
        
        # Agents work in rounds, sharing information
        num_rounds = self.capabilities.get("coordination_rounds", 2)
        
        for round_idx in range(num_rounds):
            round_results = []
            
            for agent in self.agents:
                # Each agent sees messages from peers
                peer_context = {
                    **(context or {}),
                    "round": round_idx,
                    "peer_messages": [
                        m for m in self.shared_messages
                        if m.sender_id != agent.agent_id
                    ]
                }
                
                # Agent executes task with peer context
                result = agent.execute_task(task, peer_context)
                round_results.append(result)
                
                # Share result with peers if successful
                if result.success:
                    message = Message(
                        sender_id=agent.agent_id,
                        content=result.output,
                        message_type="task_result",
                        metadata={"round": round_idx}
                    )
                    self._broadcast_message(agent, message)
            
            # Agents can adapt based on peer results in next round
            results.extend(round_results)
        
        return results
    
    def _consensus_aggregation(self, results: List[TaskResult]) -> TaskResult:
        """
        Aggregate results using consensus mechanism.
        
        Args:
            results: List of TaskResults from agents
            
        Returns:
            Consensus TaskResult
        """
        successful_results = [r for r in results if r.success]
        total_tokens = sum(r.tokens_used for r in results) + self.tokens_used
        
        if successful_results:
            # Simple consensus: majority vote or most recent
            # In real implementation, would use more sophisticated consensus
            self.tasks_completed += len(successful_results)
            
            # Use the most common result (simplified voting)
            final_output = successful_results[-1].output  # Use latest
            
            return TaskResult(
                success=True,
                output=final_output,
                tokens_used=total_tokens,
                metadata={
                    "architecture": "decentralized",
                    "num_agents": self.num_agents,
                    "successful_results": len(successful_results),
                    "failed_results": len(results) - len(successful_results),
                    "messages_exchanged": len(self.shared_messages),
                    "communication_overhead": self.tokens_used,
                }
            )
        else:
            self.errors_count += len(results)
            return TaskResult(
                success=False,
                output=None,
                tokens_used=total_tokens,
                error="No agents reached consensus",
                metadata={
                    "architecture": "decentralized",
                    "num_agents": self.num_agents,
                }
            )
    
    def execute_task(self, task: Any, context: Optional[Dict[str, Any]] = None) -> TaskResult:
        """
        Execute task with decentralized coordination.
        
        Agents work autonomously but share information through peer-to-peer
        communication to reach consensus.
        
        Args:
            task: The task to execute
            context: Optional context information
            
        Returns:
            TaskResult containing consensus result
        """
        # Reset shared state
        self.shared_messages = []
        
        # Execute with peer-to-peer coordination
        results = self._peer_to_peer_coordination(task, context)
        
        # Aggregate using consensus
        return self._consensus_aggregation(results)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics from all peer agents."""
        base_metrics = super().get_metrics()
        
        # Aggregate agent metrics
        agent_metrics = [agent.get_metrics() for agent in self.agents]
        base_metrics["agents"] = agent_metrics
        base_metrics["total_agent_tokens"] = sum(a["tokens_used"] for a in agent_metrics)
        base_metrics["communication_overhead"] = self.tokens_used
        base_metrics["messages_exchanged"] = len(self.shared_messages)
        
        return base_metrics
