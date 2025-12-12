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
)
from .metrics import (
    CoordinationMetrics,
    calculate_efficiency,
    calculate_overhead,
    calculate_error_amplification,
    calculate_redundancy,
)
from .models import ArchitectureSelector

__all__ = [
    "Agent",
    "SingleAgent",
    "IndependentMultiAgent",
    "CentralizedMultiAgent",
    "DecentralizedMultiAgent",
    "HybridMultiAgent",
    "CoordinationMetrics",
    "calculate_efficiency",
    "calculate_overhead",
    "calculate_error_amplification",
    "calculate_redundancy",
    "ArchitectureSelector",
]
