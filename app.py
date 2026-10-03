import streamlit as st
import asyncio
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent / "src"))
# Import your backend logic
from researcher import run_research_agent
from synthesizer import run_synthesis_agent
from pdf_generator import generate_pdf_report

# --- 1. UI Configuration & State Management ---
st.set_page_config(
    page_title="AI Competitive Intelligence", page_icon="🕵️", layout="centered"
)

# Initialize session state variables so the UI remembers when a report is done
if "report_ready" not in st.session_state:
    st.session_state.report_ready = False
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None


def reset_app():
    """Clears the session state to reset the UI to a blank slate."""
    st.session_state.report_ready = False
    st.session_state.pdf_bytes = None
    st.rerun()


# --- 2. The Core Execution Pipeline ---
async def generate_full_report(primary, comp1, comp2, status_container):
    # Assemble the companies list
    companies = [
        {"name": primary["name"], "url": primary["url"], "type": "Primary Company"},
        {"name": comp1["name"], "url": comp1["url"], "type": "Competitor"},
    ]
    if comp2["name"] and comp2["url"]:
        companies.append(
            {"name": comp2["name"], "url": comp2["url"], "type": "Competitor"}
        )

    # Phase 1: Research
    status_container.update(
        label=f"🕵️ Researching {len(companies)} companies in parallel...",
        state="running",
    )
    tasks = [
        run_research_agent(company_name=c["name"], url=c["url"]) for c in companies
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    final_report = {
        "report_title": "Market Landscape",
        "primary_company": {},
        "competitors": [],
    }
    for company_info, research_data in zip(companies, results):
        if isinstance(research_data, Exception):
            st.error(f"Failed to research {company_info['name']}: {research_data}")
            continue

        data_dict = research_data.model_dump()
        data_dict["name"] = company_info["name"]
        data_dict["url"] = company_info["url"]

        if company_info["type"] == "Primary Company":
            final_report["primary_company"] = data_dict
        else:
            final_report["competitors"].append(data_dict)

    try:
        reports_dir = Path("reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        research_path = reports_dir / "market_research_report.json"
        with open(research_path, "w", encoding="utf-8") as f:
            json.dump(final_report, f, indent=2)
    except OSError as e:
        raise RuntimeError(
            f"Failed to write research data to disk. Check permissions: {e}"
        )

    # Ensure the file actually exists and is a file before synthesis
    if not research_path.is_file():
        raise FileNotFoundError(
            f"The research file '{research_path}' could not be found for synthesis."
        )

    # Phase 2: Synthesis
    status_container.update(
        label="🧠 Synthesizing strategy and building SWOT analysis..."
    )
    strategy_report = await run_synthesis_agent(research_path)

    strategy_path = reports_dir / "final_strategy_report.json"
    try:
        with open(strategy_path, "w", encoding="utf-8") as f:
            f.write(strategy_report.model_dump_json(indent=2))
    except OSError as e:
        raise RuntimeError(f"Failed to write final strategy report to disk: {e}")

    # Ensure the strategy file exists before PDF generation
    if not strategy_path.is_file():
        raise FileNotFoundError(
            f"The strategy file '{strategy_path}' could not be found for PDF generation."
        )

    # Phase 3: PDF Generation
    status_container.update(label="📄 Preparing downloadable PDF layout...")
    pdf_path = reports_dir / "competitive_strategy_report.pdf"
    generate_pdf_report(
        market_research_path=research_path,
        strategy_report_path=strategy_path,
        output_pdf_path=pdf_path,
    )

    status_container.update(label="✅ Report Generation Complete!", state="complete")

    # Read the PDF into memory so Streamlit can offer it as a download
    with open(pdf_path, "rb") as f:
        return f.read()


# --- 3. The Frontend Layout ---
st.title("🕵️ AI Competitive Strategy Agent")
st.markdown(
    "Enter your company and competitors to generate a comprehensive 1-page PDF strategy report."
)

# View A: The Input Form
if not st.session_state.report_ready:
    with st.form("research_form"):
        st.subheader("Your Company")
        col1, col2 = st.columns(2)
        with col1:
            primary_name = st.text_input("Company Name", placeholder="e.g., Stripe")
        with col2:
            primary_url = st.text_input("Website URL", placeholder="https://stripe.com")

        st.subheader("Competitor 1")
        col3, col4 = st.columns(2)
        with col3:
            comp1_name = st.text_input("Competitor 1 Name", placeholder="e.g., Square")
        with col4:
            comp1_url = st.text_input(
                "Competitor 1 URL", placeholder="https://squareup.com"
            )

        st.subheader("Competitor 2 (Optional)")
        col5, col6 = st.columns(2)
        with col5:
            comp2_name = st.text_input("Competitor 2 Name", placeholder="e.g., Adyen")
        with col6:
            comp2_url = st.text_input(
                "Competitor 2 URL", placeholder="https://adyen.com"
            )

        submit = st.form_submit_button("Generate Strategy Report", type="primary")

    if submit:
        # Validation
        if not primary_name or not primary_url or not comp1_name or not comp1_url:
            st.error(
                "Please fill in the details for Your Company and at least Competitor 1."
            )
        else:
            primary = {"name": primary_name, "url": primary_url}
            comp1 = {"name": comp1_name, "url": comp1_url}
            comp2 = {"name": comp2_name, "url": comp2_url}

            # This status box will be passed into the async function to update dynamically
            status_box = st.status("Starting AI Agents...", expanded=True)

            try:
                # Streamlit is synchronous, so we use asyncio.run to execute our async pipeline
                pdf_bytes = asyncio.run(
                    generate_full_report(primary, comp1, comp2, status_box)
                )

                # Update state variables and reload the UI to show the download button
                st.session_state.pdf_bytes = pdf_bytes
                st.session_state.report_ready = True
                st.rerun()

            except Exception as e:
                status_box.update(label="❌ Error generating report", state="error")
                st.error(f"An error occurred: {e}")

# View B: The Download Screen
if st.session_state.report_ready:
    st.success("🎉 Your Competitive Strategy Report is ready!")

    col_down, col_reset = st.columns([1, 1])
    with col_down:
        st.download_button(
            label="⬇️ Download PDF Report",
            data=st.session_state.pdf_bytes,
            file_name="Competitive_Strategy_Report.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )
    with col_reset:
        st.button(
            "Start New Research (Reset)", on_click=reset_app, use_container_width=True
        )
