"""Lagos traffic congestion levels."""

from enum import Enum


class TrafficLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HEAVY = "heavy"
    GRIDLOCK = "gridlock"

    @property
    def multiplier(self) -> float:
        return {
            TrafficLevel.LOW: 1.0,
            TrafficLevel.MODERATE: 1.15,
            TrafficLevel.HEAVY: 1.35,
            TrafficLevel.GRIDLOCK: 1.60,
        }[self]
