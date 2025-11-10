from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class Point:
    name: str
    kind: str
    flow_lpm: float
    p_min_dyn_kpa: float
    count: int = 1

@dataclass
class HeaterModel:
    brand: str
    model: str
    q_ref_lpm: float
    dT_ref_C: float
    power_kw: float
    q_min_on_lpm: float
    p_min_dyn_kpa: float
    dp_curve: Optional[Dict[float, float]] = None
