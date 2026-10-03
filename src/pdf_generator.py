import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML


def generate_pdf_report(
    market_research_path: str,
    strategy_report_path: str,
    output_pdf_path: str = "competitive_report.pdf",
    templates_dir: str = "templates",
) -> str:
    """
    Renders the JSON strategy report into a downloadable PDF using Jinja2 and WeasyPrint.
    """
    # 1. Load source data
    try:
        with open(market_research_path, "r", encoding="utf-8") as f:
            market_data = json.load(f)
    except FileNotFoundError:
        print(
            f"Error: Could not find '{market_research_path}' when attempting to open it."
        )
    except Exception as e:
        print(f"An unexpected error occurred during pdf generation: {e}")

    try:
        with open(strategy_report_path, "r", encoding="utf-8") as f:
            strategy_data = json.load(f)
    except FileNotFoundError:
        print(
            f"Error: Could not find '{strategy_report_path}' when attempting to open it."
        )
    except Exception as e:
        print(f"An unexpected error occurred during pdf generation: {e}")

    primary_name = market_data.get("primary_company", {}).get("name", "Target Company")
    competitor_names = [c["name"] for c in market_data.get("competitors", [])]

    # 2. Setup Jinja2 Environment
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template("report_template.html")

    # 3. Render HTML
    rendered_html = template.render(
        primary_company_name=primary_name,
        competitor_names=competitor_names,
        report=strategy_data,
    )

    # 4. Generate PDF via WeasyPrint
    print(f"📄 Compiling PDF deliverable to {output_pdf_path}...")
    HTML(string=rendered_html).write_pdf(output_pdf_path)
    print("✅ PDF successfully generated!")

    return output_pdf_path
