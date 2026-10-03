import os
import json
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from typing import List, Dict


class CompetitorCapability(BaseModel):
    competitor_name: str
    capability: str


class FeatureComparison(BaseModel):
    feature_name: str
    primary_company_capability: str = Field(
        description="How the primary company handles this feature."
    )
    competitors_capabilities: List[CompetitorCapability] = Field(
        description="A dictionary mapping each competitors's name to their capability for this feature."
    )


class SWOTAnalysis(BaseModel):
    strengths: List[str] = Field(
        description="Internal advantages of the primary company vs competitors."
    )
    weaknesses: List[str] = Field(
        description="Internal disadvantages or missing features."
    )
    opportunities: List[str] = Field(
        description="External market gaps or competitor vulnerabilities."
    )
    threats: List[str] = Field(
        description="External risks from competitor positioning or market shifts."
    )


class ActionItem(BaseModel):
    title: str
    timeframe: str = Field(description="30, 60, or 90 days")
    action_type: str = Field(
        description="Experiment, Strategic Pivot, or Positioning Adjustment"
    )
    expected_impact: str
    execution_steps: List[str]


class CompetitorClassification(BaseModel):
    competitor_name: str
    classification: str = Field(description="Either 'Direct' or 'Indirect'")


class StrategyReport(BaseModel):
    executive_summary: str = Field(
        description="A concise 1-page overview highlighting key takeaways, threats, and market opportunities."
    )
    competitor_classifications: List[CompetitorClassification] = Field(
        description="Dictionary mapping each competitor name to either 'Direct' or 'Indirect'."
    )
    product_feature_matrix: List[FeatureComparison]
    swot_analysis: SWOTAnalysis
    actionable_recommendations: List[ActionItem] = Field(min_length=3, max_length=5)


async def run_synthesis_agent(research_json_path: str) -> StrategyReport:
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Load the raw data gathered by the research agents
    with open(research_json_path, "r", encoding="utf-8") as f:
        raw_market_data = f.read()

    instructions = """
    You are a Principal Market Intelligence Analyst.
    Review the provided market research data containing a primary company and its competitors.

    Synthesize the data into a strategic report:
    1. Classify competitors as direct or indirect based on audience and core problem.
    2. Build a feature comparison matrix benchmark.
    3. Draft a SWOT analysis from the primary company's perspective against the competitors.
    4. Propose 3-5 concrete actionable recommendations for the primary company.
    5. Write a high-level executive summary.

    Base all analysis strictly on the provided JSON data. Do not invent capabilities.
    """

    print("🧠 Synthesis Agent is synthesizing the strategy report...")

    # Execute the synthesis step, strictly enforcing the StrategyReport schema
    response = await client.responses.parse(
        model="gpt-6-luna",
        instructions=instructions,
        input=f"Market Data:\n{raw_market_data}",
        text_format=StrategyReport,
    )

    return response.output_parsed
