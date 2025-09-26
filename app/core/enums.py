"""
Enums for the routing engine
"""

from enum import Enum

class Domain(Enum):
    """Prompt domain classification"""
    CODING = "coding"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    GENERAL = "general"

class Complexity(Enum):
    """Prompt complexity level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
