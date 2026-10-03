from src.researcher import run_research_agent
from src.synthesizer import run_synthesis_agent
from src.pdf_generator import generate_pdf_report
import asyncio
import json
from pathlib import Path


async def main():
    companies_to_research = [
        {"name": "Stripe", "url": "https://stripe.com", "type": "Primary Company"},
        {"name": "Square", "url": "https://squareup.com", "type": "Competitor"},
        {"name": "Adyen", "url": "https://www.adyen.com", "type": "Competitor"},
    ]

    print(
        f"Agent is concurrently researching {len(companies_to_research)} companies...\n"
    )

    try:
        tasks = [
            run_research_agent(company_name=company["name"], url=company["url"])
            for company in companies_to_research
        ]

        # return_exceptions=True prevents one failed API/scrape call from killing the entire batch
        results = await asyncio.gather(*tasks, return_exceptions=True)
        print("Research Complete! Structuring final report...\n")

        final_report = {
            "report_title": "Market Landscape Research",
            "primary_company": {},
            "competitors": [],
        }

        # Map the returned Pydantic objects back to their respective roles
        for company_info, research_data in zip(companies_to_research, results):
            # Check if this specific agent task encountered an exception
            if isinstance(research_data, Exception):
                print(f"⚠️ Failed to research {company_info['name']}: {research_data}")
                continue

            # Convert the Pydantic model to a standard Python dictionary
            company_data_dict = research_data.model_dump()
            company_data_dict["name"] = company_info["name"]
            company_data_dict["url"] = company_info["url"]

            if company_info["type"] == "Primary Company":
                final_report["primary_company"] = company_data_dict
            else:
                final_report["competitors"].append(company_data_dict)

        # 4. Save the combined results to a local JSON file
        output_filename = "market_research_report.json"
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(final_report, f, indent=2)

        print(f"💾 Report saved successfully to {output_filename}")

    except OSError as e:
        print(f"File system error saving '{output_filename}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred during the research workflow: {e}")

    # 5. Run the synthesis agent
    file_path = Path(output_filename)
    try:
        # Check if the path exists AND is specifically a file (not a folder)
        if file_path.is_file():
            print("The research file exists. Proceeding with synthesis...")

            # The agent only runs if the file is confirmed to exist
            strategy_report = await run_synthesis_agent(output_filename)

            # 6. Save the final strategic output
            final_output_path = "final_strategy_report.json"
            with open(final_output_path, "w", encoding="utf-8") as f:
                f.write(strategy_report.model_dump_json(indent=2))

            print(f"🎯 Strategy synthesis complete! Saved to: {final_output_path}")

            # 7. Generating the pdf template
            generate_pdf_report(
                market_research_path="market_research_report.json",
                strategy_report_path="final_strategy_report.json",
                output_pdf_path="market_strategy_report.pdf",
            )

        else:
            # Stop execution cleanly if the file is missing
            print(f"Error: The research file '{output_filename}' does not exist.")

    except FileNotFoundError:
        # Failsafe in case the file is deleted a split second after the is_file() check
        print(f"Error: Could not find '{output_filename}' when attempting to open it.")
    except Exception as e:
        # Catches OpenAI API timeouts, Pydantic validation errors, or missing permissions
        print(f"An unexpected error occurred during synthesis: {e}")


if __name__ == "__main__":
    asyncio.run(main())
