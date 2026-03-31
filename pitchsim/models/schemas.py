from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


FunnelStage = Literal["unaware", "aware", "interested", "objecting", "convinced", "advocate"]
NetworkType = Literal["small_world", "scale_free", "clustered", "random"]


class SimulationConfig(BaseModel):
    sim_id: str
    product_brief: str
    target_market: str
    price_point: str
    pitch_variants: list[str] = Field(default_factory=list, max_length=3)

    population_size: int = 80
    num_ticks: int = 20
    network_type: NetworkType = "small_world"
    use_mock_llm: bool = True


class MindOutput(BaseModel):
    new_stage: FunnelStage
    conviction_delta: float = Field(ge=-0.3, le=0.3)
    objection_text: str | None
    response_text: str
    mutated_idea: str
    reasoning: str
    would_advocate: bool


class TickSnapshot(BaseModel):
    tick: int
    total_ticks: int
    stage_counts: dict[FunnelStage, int]
    latest_interactions: list[dict[str, Any]] = Field(default_factory=list)
    graph_delta: dict[str, Any] = Field(default_factory=dict)

