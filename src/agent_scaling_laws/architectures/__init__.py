"""Agent architecture implementations."""

from .base import Agent, TaskResult, Message
from .single_agent import SingleAgent
from .independent import IndependentMultiAgent
from .centralized import CentralizedMultiAgent
from .decentralized import DecentralizedMultiAgent
from .hybrid import HybridMultiAgent

__all__ = [
    "Agent",
    "TaskResult",
    "Message",
    "SingleAgent",
    "IndependentMultiAgent",
    "CentralizedMultiAgent",
    "DecentralizedMultiAgent",
    "HybridMultiAgent",
]
