from __future__ import annotations

import hashlib

from pitchsim.agents.agent import Agent
from pitchsim.models.schemas import MindOutput


class MockMindEngine:
    """
    Deterministic, zero-cost replacement for an LLM.
    Goal: always return valid `MindOutput` so the whole product works without keys.
    """

    def reason(self, agent: Agent, idea: str, speaker: Agent) -> MindOutput:
        seed = _stable_int(f"{agent.id}:{speaker.id}:{idea[:64]}")

        # Simple deterministic "fit" score: archetype + comfort - switching friction.
        archetype_bias = {
            "early_adopter": 0.18,
            "influencer": 0.10,
            "analyst": 0.06,
            "conformist": 0.02,
            "skeptic": -0.10,
        }[agent.archetype]

        switching_penalty = {"low": 0.02, "medium": 0.08, "high": 0.14}[agent.switching_cost]
        price_penalty = 0.06 if any(tok in agent.current_solution.lower() for tok in ["excel", "whatsapp"]) else 0.03

        delta = archetype_bias + 0.12 * agent.tech_comfort + 0.08 * agent.risk_tolerance - switching_penalty - price_penalty
        wobble = ((seed % 31) - 15) / 1000.0  # -0.015..+0.016 deterministic noise
        conviction_delta = max(-0.3, min(0.3, delta + wobble))

        new_score = max(0.0, min(1.0, agent.conviction_score + conviction_delta))

        new_stage = _score_to_stage(new_score)
        objection = None
        if new_stage in ("objecting",) or (new_stage == "interested" and conviction_delta < 0.02):
            objection = _pick_objection(seed, agent)

        response = _response_text(seed, objection)
        mutated = _mutate_idea(seed, idea)
        reasoning = _reasoning_text(conviction_delta, objection)

        return MindOutput(
            new_stage=new_stage,
            conviction_delta=float(round(conviction_delta, 3)),
            objection_text=objection,
            response_text=response,
            mutated_idea=mutated,
            reasoning=reasoning,
            would_advocate=new_stage in ("advocate",) or (new_stage == "convinced" and conviction_delta > 0.08),
        )


def _stable_int(s: str) -> int:
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def _score_to_stage(score: float):
    if score < 0.12:
        return "unaware"
    if score < 0.28:
        return "aware"
    if score < 0.52:
        return "interested"
    if score < 0.70:
        return "objecting"
    if score < 0.88:
        return "convinced"
    return "advocate"


def _pick_objection(seed: int, agent: Agent) -> str:
    objections = [
        "The price feels high; I’d need a free trial or proof first.",
        "I already have a workaround; switching sounds like effort.",
        "I’m not sure I trust a new product yet—what if it shuts down?",
        "Does this integrate with what I already use?",
        "I’m worried it will be too complex for my team.",
    ]
    idx = (seed + int(agent.tech_comfort * 100)) % len(objections)
    return objections[idx]


def _response_text(seed: int, objection: str | None) -> str:
    if objection:
        return f"I’m interested, but {objection.lower()}"
    templates = [
        "That actually sounds useful. Tell me more about how it works.",
        "Okay, I can see the value if it saves time week to week.",
        "If it’s simple to set up, I’d try it.",
        "This could be a good fit for us—what’s the next step?",
    ]
    return templates[seed % len(templates)]


def _mutate_idea(seed: int, idea: str) -> str:
    prefixes = [
        "Basically it's",
        "It’s kind of like",
        "Think of it as",
        "The idea is",
    ]
    p = prefixes[seed % len(prefixes)]
    short = idea.strip().replace("\n", " ")
    if len(short) > 160:
        short = short[:157].rstrip() + "..."
    return f"{p} {short}"


def _reasoning_text(conviction_delta: float, objection: str | None) -> str:
    if objection:
        return f"I see potential, but my main blocker is: {objection}"
    if conviction_delta > 0.08:
        return "This feels credible and valuable enough that I’d seriously consider it."
    if conviction_delta > 0.02:
        return "I’m cautiously positive; I want to understand setup and proof."
    return "I’m unconvinced so far; I’d need clearer ROI and lower switching risk."

