from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


FunnelStage = Literal["unaware", "aware", "interested", "objecting", "convinced", "advocate"]
SwitchingCost = Literal["low", "medium", "high"]
Archetype = Literal["early_adopter", "skeptic", "conformist", "influencer", "analyst"]


@dataclass(slots=True)
class Agent:
    id: str
    name: str
    age: int
    job_title: str
    archetype: Archetype

    tech_comfort: float  # 0.0–1.0
    risk_tolerance: float  # 0.0–1.0
    budget_authority: bool

    current_solution: str
    switching_cost: SwitchingCost

    funnel_stage: FunnelStage = "unaware"
    conviction_score: float = 0.0  # 0.0–1.0
    active_objection: str | None = None

    idea_version: str = ""
    memory: list[str] = field(default_factory=list)  # last few conversation summaries
    trust_network: list[str] = field(default_factory=list)  # agent ids

