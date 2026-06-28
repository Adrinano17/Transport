"""Transport mode available in Lagos."""

from enum import Enum


class TransportType(str, Enum):
    TAXI = "taxi"
    BOLT = "bolt"
    UBER = "uber"
    KEKE = "keke"
    BRT = "brt"
    DANFO = "danfo"
