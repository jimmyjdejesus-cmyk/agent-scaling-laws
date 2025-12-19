"""
Agent Scaling Laws - Implementation of coordination architectures and scaling principles
for multi-agent systems based on the paper "Towards a Science of Scaling Agent Systems".
"""

__version__ = "0.1.0"

from .architectures import (
    Agent,
    SingleAgent,
    IndependentMultiAgent,
    CentralizedMultiAgent,
    DecentralizedMultiAgent,
    HybridMultiAgent,
    TaskResult,
    Message,
)
from .metrics import (
    CoordinationMetrics,
    calculate_efficiency,
    calculate_overhead,
    calculate_error_amplification,
    calculate_redundancy,
)
from .models import (
    ArchitectureSelector,
    TaskCharacteristics,
    AgentCapabilities,
)

__all__ = [
    "Agent",
    "SingleAgent",
    "IndependentMultiAgent",
    "CentralizedMultiAgent",
    "DecentralizedMultiAgent",
    "HybridMultiAgent",
    "TaskResult",
    "Message",
    "CoordinationMetrics",
    "calculate_efficiency",
    "calculate_overhead",
    "calculate_error_amplification",
    "calculate_redundancy",
    "ArchitectureSelector",
    "TaskCharacteristics",
    "AgentCapabilities",
]
