# AI Competitive Strategy Agent 🕵️

An automated market intelligence and competitor research engine built with Python, Streamlit, and OpenAI. The agent accepts a primary company alongside one or two rivals, executes targeted web research concurrently, synthesizes a strategic SWOT analysis and feature comparison matrix, and outputs a publication-ready PDF deliverable.

---

## What This App Does

The application runs an end-to-end, three-phase market intelligence pipeline:

1. **Parallel Web Research:** Gathers verified, public web data across all selected companies simultaneously via OpenAI's search-enabled agent framework.
2. **Strategic Synthesis:** Analyzes the raw unstructured research through a dedicated Principal Analyst prompt to produce:
   * **Executive Summary:** Core takeaways and market outlook.
   * **Competitor Classification:** Classifies rivals as direct or indirect competitors.
   * **Product & Feature Matrix:** Side-by-side benchmark of capabilities.
   * **SWOT Analysis:** Strengths, weaknesses, opportunities, and threats mapped from the primary company's perspective.
   * **Actionable Recommendations:** 3 to 5 concrete 30-to-90-day strategic initiatives.
3. **PDF Generation:** Renders the structured data into an executive-styled HTML/CSS layout and compiles it into a downloadable PDF report.

---

## Prerequisites

* Python 3.11+
* [uv](https://docs.astral.sh/uv/) installed on your machine
* An [OpenAI API Key](https://platform.openai.com/api-keys)

---

## Getting Started

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd market_research_agent
```

### 2.Set Up the Environment with uv
Initialize the environment and sync all project dependencies:

```bash
uv sync
```
If you are initializing from scratch or installing dependencies manually:
```bash
uv add openai streamlit pydantic jinja2 weasyprint python-dotenv
```

### 3. Configure Your Environment Variables
Create a .env file in the root directory:

```bash
touch .env
```
Add your OpenAI API key to .env:
```bash
OPENAI_API_KEY="your-actual-openai-api-key-here"
```

### 4. Running the Application
```bash
uv run streamlit run app.py
```
Streamlit will start a local development server and open http://localhost:8501 in your browser.

### Usage Guide
1. Enter Your Company: Provide your company's name and primary website URL.
2. Enter Competitors: Add Competitor 1 (required) and Competitor 2 (optional).
3. Generate: Click Generate Strategy Report. The dynamic status bar will track progress:
4. Researching companies in parallel
5. Synthesizing strategic matrix & SWOT
6. Formatting the PDF deliverable
7. Download: Click Download PDF Report to save the compiled strategy memo directly to your device.
8. Reset: Click Start New Research to clear the session state and run an analysis on a new set of companies
