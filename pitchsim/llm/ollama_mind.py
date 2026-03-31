from __future__ import annotations

from pitchsim.agents.agent import Agent
from pitchsim.models.schemas import MindOutput


class OllamaMindEngine:
    """
    Local-LLM mind engine (Ollama) using LangChain.

    This is intentionally isolated behind an engine interface so we can swap:
    - MockMindEngine (dev, deterministic)
    - OllamaMindEngine (local, no billing)
    - Cloud providers later (Anthropic/OpenAI)
    """

    def __init__(
        self,
        model: str = "llama3.1:8b",
        base_url: str | None = None,
        temperature: float = 0.2,
        timeout_s: float = 60.0,
    ) -> None:
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.timeout_s = timeout_s

    def reason(self, agent: Agent, idea: str, speaker: Agent) -> MindOutput:
        """
        Calls local Ollama model and returns structured MindOutput.
        """
        # Lazy imports so the repo runs even if Ollama deps aren't installed yet.
        from langchain_core.output_parsers import PydanticOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_ollama import ChatOllama

        parser = PydanticOutputParser(pydantic_object=MindOutput)

        system = (
            "You are {name}, {age} years old, {job_title}.\n"
            "Archetype: {archetype}. Tech comfort: {tech_comfort}/1.0. Risk tolerance: {risk_tolerance}/1.0.\n"
            "You currently use: {current_solution}. Switching cost: {switching_cost}.\n"
            "Respond as this person would — with their doubts, habits, and priorities.\n"
            "Return ONLY valid JSON.\n"
            "{format_instructions}"
        )

        human = (
            "{speaker_name} just told you about a product:\n"
            "\"{idea_version}\"\n\n"
            "Price: {price_point}\n\n"
            "Reason honestly:\n"
            "1) Do I actually have this problem?\n"
            "2) Is this believable?\n"
            "3) Would I pay?\n"
            "4) Biggest objection?\n"
            "5) Would I mention to others?\n"
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", human),
            ]
        )

        llm = ChatOllama(
            model=self.model,
            base_url=self.base_url,
            temperature=self.temperature,
            timeout=self.timeout_s,
        )

        chain = prompt | llm | parser

        # Note: `Agent` currently doesn't store price; engine will pass it later.
        # For now we keep price_point blank; simulation will supply config.price_point.
        return chain.invoke(
            {
                "format_instructions": parser.get_format_instructions(),
                "name": agent.name,
                "age": agent.age,
                "job_title": agent.job_title,
                "archetype": agent.archetype,
                "tech_comfort": agent.tech_comfort,
                "risk_tolerance": agent.risk_tolerance,
                "current_solution": agent.current_solution,
                "switching_cost": agent.switching_cost,
                "speaker_name": speaker.name,
                "idea_version": idea,
                "price_point": "",
            }
        )

