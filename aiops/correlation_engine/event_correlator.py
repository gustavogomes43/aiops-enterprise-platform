from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class EventType(Enum):
    NETWORK_LATENCY = "network_latency"
    DATABASE = "database"
    API = "api"
    INFRASTRUCTURE = "infrastructure"


class EventSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Event:
    id: str
    timestamp: datetime
    type: EventType
    severity: EventSeverity
    source: str
    message: str


class CorrelationEngine:
    def __init__(self, redis_host="localhost"):
        self.redis_host = redis_host
        self.events = []

    def add_event(self, event: Event):
        """
        Adiciona evento ao buffer de correlação
        """
        self.events.append(event)

    def correlate(self):
        """
        Simula correlação de eventos
        """
        if len(self.events) > 5:
            return "🔥 Root Cause Detected"

        return "Analyzing..."