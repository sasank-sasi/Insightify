from bs4 import BeautifulSoup
import requests
from typing import Dict, List
import json
from datetime import datetime
import re
import os

class EnhancedResourceAssetAgent:
    def __init__(self, use_cases: List[str], industry: str):
        self.use_cases = use_cases
        self.industry = industry
        self.sources = {
            "datasets": [
                {"source": "kaggle", "url": f"https://www.kaggle.com/search?q={use_case.replace(' ', '+')}+{industry}+dataset", "relevance_score": 0.8, "type": "dataset"} for use_case in use_cases
            ],
            "papers": [
                {"source": "arxiv", "url": f"https://arxiv.org/search/?query={use_case.replace(' ', '+')}+{industry}&searchtype=all", "relevance_score": 0.9, "type": "paper"} for use_case in use_cases
            ],
            "implementations": [
                {"source": "github", "url": f"https://github.com/search?q={use_case.replace(' ', '+')}+{industry}", "relevance_score": 0.7, "type": "implementation"} for use_case in use_cases
            ]
        }
        
        self.report_sources = [
            {"source": "mckinsey", "url": f"https://www.mckinsey.com/search?q={use_case.replace(' ', '+')}+{industry}+AI+implementation", "type": "report", "relevance_score": 0.9} for use_case in use_cases
        ] + [
            {"source": "deloitte", "url": f"https://www2.deloitte.com/search?q={use_case.replace(' ', '+')}+{industry}+AI+implementation", "type": "report", "relevance_score": 0.85} for use_case in use_cases
        ] + [
            {"source": "gartner", "url": f"https://www.gartner.com/search?q={use_case.replace(' ', '+')}+{industry}+AI+implementation", "type": "report", "relevance_score": 0.9} for use_case in use_cases
        ]

    def collect_resources(self, use_case: str, industry: str) -> Dict:
        """Collect all relevant resources for a use case"""
        resources = {
            "datasets": self.search_datasets(use_case, industry),
            "papers": self.search_papers(use_case),
            "implementations": self.search_implementations(use_case),
            "reports": self.search_industry_reports(use_case, industry)
        }
        return resources

    def search_datasets(self, use_case: str, industry: str) -> List[Dict]:
        """Search for relevant datasets across multiple sources"""
        datasets = []
        search_term = f"{use_case} {industry} dataset"
        
        try:
            for source in self.sources["datasets"]:
                query = f"{source['url']}"
                datasets.append({
                    "source": source["source"],
                    "url": query,
                    "relevance_score": source["relevance_score"],
                    "type": "dataset"
                })
            return datasets
        except Exception as e:
            return [{"error": f"Dataset search failed: {str(e)}"}]

    def search_papers(self, use_case: str) -> List[Dict]:
        """Search for relevant research papers and implementations"""
        papers = []
        try:
            query = f"{use_case} AI ML implementation"
            papers.extend(self._search_arxiv(query))
            papers.extend(self._search_paperswithcode(query))
            return papers
        except Exception as e:
            return [{"error": f"Paper search failed: {str(e)}"}]

    def search_implementations(self, use_case: str) -> List[Dict]:
        """Search for code implementations and examples"""
        try:
            query = f"{use_case.replace(' ', '-').lower()}"
            github_url = f"{self.sources['implementations'][0]['url']}/{query}"
            return [{
                "source": "github",
                "url": github_url,
                "type": "implementation",
                "relevance_score": self.sources['implementations'][0]['relevance_score']
            }]
        except Exception as e:
            return [{"error": f"Implementation search failed: {str(e)}"}]

    def search_industry_reports(self, use_case: str, industry: str) -> List[Dict]:
        """Search for industry reports and whitepapers"""
        reports = []
        search_term = f"{use_case} {industry} AI implementation"
        
        try:
            for source in self.report_sources:
                query = f"{source['url']}?q={search_term.replace(' ', '+')}"
                reports.append({
                    "source": source["source"],
                    "url": query,
                    "type": "report",
                    "relevance_score": source["relevance_score"]
                })
            return reports
        except Exception as e:
            return [{"error": f"Report search failed: {str(e)}"}]

    def _calculate_relevance_score(self, use_case: str, source: str) -> float:
        """Calculate relevance score based on source and use case"""
        base_scores = {
            "kaggle": 0.8,
            "huggingface": 0.9,
            "github": 0.7,
            "mckinsey": 0.9,
            "deloitte": 0.85,
            "gartner": 0.9
        }
        return base_scores.get(source, 0.5)

    def generate_markdown_report(self, resources: Dict, use_case: str) -> str:
        """Generate a formatted markdown report of collected resources"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""# Resource Collection Report for {use_case}
Generated on: {timestamp}

## Datasets
"""
        for dataset in resources.get("datasets", []):
            report += f"- [{dataset['source']}]({dataset['url']}) (Relevance: {dataset['relevance_score']})\n"
        
        report += "\n## Research Papers\n"
        for paper in resources.get("papers", []):
            if 'url' in paper:
                report += f"- [{paper.get('title', 'Untitled')}]({paper['url']})\n"
            else:
                report += f"- Error: {paper['error']}\n"
        
        report += "\n## Implementations\n"
        for impl in resources.get("implementations", []):
            report += f"- [GitHub Implementation]({impl['url']})\n"
        
        report += "\n## Industry Reports\n"
        for report_item in resources.get("reports", []):
            report += f"- [{report_item['source'].title()}]({report_item['url']})\n"
        
        return report

    def save_resources(self, resources, use_case, markdown_content, output_dir):
        try:
            # Debugging: Print the resources to ensure they have the expected structure
            print("Resources to save:", resources)

            # Flatten the resources
            flat_resources = []
            for category, items in resources.items():
                flat_resources.extend(items)

            # Save JSON
            os.makedirs(output_dir, exist_ok=True)
            json_filename = os.path.join(output_dir, f"{use_case.replace(' ', '_')}_resources.json")
            with open(json_filename, 'w') as f:
                json.dump(flat_resources, f, indent=4)

            # Append to Markdown content
            markdown_content += self.generate_markdown_report(resources, use_case)

            # Save Markdown
            md_filename = os.path.join(output_dir, f"{use_case.replace(' ', '_')}_resources.md")
            with open(md_filename, 'w') as f:
                f.write(markdown_content)

            return {"json": json_filename, "markdown_content": markdown_content}
        except Exception as e:
            return {"error": f"Failed to save resources: {str(e)}"}

def load_use_cases_from_markdown(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            use_cases = re.findall(r"\*\*Use Case \d+: (.+?)\*\*", content)
            return use_cases
    except Exception as e:
        print(f"Error loading use cases from Markdown file: {str(e)}")
        return []

# Example Usage
if __name__ == "__main__":
    industry = input("Enter the industry: ")

    # Load use cases from the Markdown file
    use_cases_file_path = "/Users/sasanksasi/Downloads/project/intern/output/use_cases.md"
    use_cases = load_use_cases_from_markdown(use_cases_file_path)

    agent = EnhancedResourceAssetAgent(use_cases, industry)

    # Initialize markdown content
    markdown_content = f"# Use Cases for {industry}\n\n"

    for use_case in use_cases:
        # Collect resources for each use case
        resources = agent.collect_resources(use_case, industry)

        # Save resources and update markdown content
        use_case_folder = os.path.join("/Users/sasanksasi/Downloads/project/intern/output/resources", use_case.replace(' ', '_'))
        os.makedirs(use_case_folder, exist_ok=True)

        result = agent.save_resources(resources, use_case, markdown_content, use_case_folder)
        markdown_content = result["markdown_content"]
        print(f"Resources for '{use_case}' saved to: {result['json']}")

    # Save the combined markdown content to a single file
    output_dir = "/Users/sasanksasi/Downloads/project/intern/output"
    md_filename = os.path.join(output_dir, "collected_resources.md")
    with open(md_filename, 'w') as f:
        f.write(markdown_content)
    print(f"Combined Markdown file saved to: {md_filename}")
    
    json_filename = os.path.join(output_dir, "collected_resources.json")
    json_content = {"content": markdown_content}

    with open(json_filename, 'w') as f:
        json.dump(json_content, f, indent=4)