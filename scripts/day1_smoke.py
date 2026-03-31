from __future__ import annotations

import json
import uuid

from pitchsim.agents.agent import Agent
from pitchsim.llm.mock import MockMindEngine


def main() -> None:
    sim_id = str(uuid.uuid4())
    idea = "An AI-powered ops assistant for small restaurants that auto-tracks inventory, suggests reorders, and integrates with delivery apps."

    a = Agent(
        id=str(uuid.uuid4()),
        name="Ravi",
        age=34,
        job_title="Restaurant owner (2 locations)",
        archetype="early_adopter",
        tech_comfort=0.8,
        risk_tolerance=0.7,
        budget_authority=True,
        current_solution="Excel + WhatsApp",
        switching_cost="medium",
        funnel_stage="aware",
        conviction_score=0.55,
        idea_version=idea,
    )

    b = Agent(
        id=str(uuid.uuid4()),
        name="Priya",
        age=39,
        job_title="Restaurant manager (single location)",
        archetype="skeptic",
        tech_comfort=0.5,
        risk_tolerance=0.4,
        budget_authority=False,
        current_solution="Notebook + WhatsApp",
        switching_cost="high",
        funnel_stage="unaware",
        conviction_score=0.1,
        idea_version="",
    )

    mind = MockMindEngine()
    out = mind.reason(agent=b, idea=a.idea_version, speaker=a)

    print(f"sim_id: {sim_id}")
    print("speaker:", a)
    print("listener:", b)
    print("\nMindOutput JSON:")
    print(json.dumps(out.model_dump(), indent=2))


if __name__ == "__main__":
    main()

