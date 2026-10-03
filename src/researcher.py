import os
from openai import OpenAI, AsyncOpenAI
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class Product(BaseModel):
    name: str
    description: str
    features: List[str]


class CompanyResearch(BaseModel):
    company_name: str
    description: str
    target_customers: List[str]
    problems_solved: List[str]
    products: List[Product]
    positioning: str
    pricing_model: str
    usp: List[str]


async def run_research_agent(company_name: str, url: str) -> CompanyResearch:
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    instructions = """
    You are a market research agent.
    Your job is to research a company using publicly available information on the web.
    Research carefully and use primary sources whenever possible.
    Do not invent information. If information cannot be verified, add it to the unverified_information list.
    """

    research = await client.responses.parse(
        model="gpt-6-luna",
        instructions=instructions,
        tools=[{"type": "web_search"}],
        input=f"Research {company_name}: {url}",
        text_format=CompanyResearch,
    )

    return research.output_parsed
