import os
import sys
from dotenv import load_dotenv
from research_agent import ResearchAgent
from Market_agent import UseCaseAgent 
from resource_agent import EnhancedResourceAssetAgent
from final_proposal_agent import generate_final_proposal_groq


class AIImplementationOrchestrator:
    def __init__(self):
        load_dotenv()
        
        # Configuration
        self.company = input("Enter company name (default: Deloitte): ") or "Deloitte"
        self.industry = input("Enter industry (default: Professional Services): ") or "Professional Services"
        self.company_url = input("Enter company URL (default: https://www2.deloitte.com/us/en.html): ") or "https://www2.deloitte.com/us/en.html"
        
        # API Keys
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        if not self.tavily_api_key or not self.groq_api_key:
            raise ValueError("Missing API keys. Please check your .env file")
        
        # Base directory is the project root
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Output paths relative to base directory
        self.output_dir = os.path.join(self.base_dir, "output")
        self.proposals_dir = os.path.join(self.base_dir, "proposals")
        
        # Create directories if they don't exist
        for directory in [self.output_dir, self.proposals_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)

        # In pipe.py
    def run(self):
        print(f"\nStarting AI Implementation Analysis for {self.company}")
        
        try:
            # 1. Research Phase
            print("\n1. Running Research Agent...")
            research_agent = ResearchAgent(api_key=self.tavily_api_key)
            research_results = research_agent.search_company_info(self.company)
            website_info = research_agent.scrape_company_website(self.company_url)
            research_results.update(website_info)
            
            research_file = os.path.join(self.output_dir, "company_research.json")
            research_agent.save_to_json(research_results, research_file)
            print(f"Research results saved to: {research_file}")
            
            # 2. Market Analysis Phase
            print("\n2. Running Market Analysis...")
            market_agent = UseCaseAgent(api_key=self.tavily_api_key, groq_key=self.groq_api_key)
            trends = market_agent.analyze_trends(self.industry)
            use_cases = market_agent.generate_use_cases(self.industry)
            
            market_results = {
                "trends": trends,
                "use_cases": use_cases
            }
            
            market_file = os.path.join(self.output_dir, "market_analysis.json")
            market_agent.save_to_json(market_results, market_file)
            print(f"Market analysis saved to: {market_file}")
            
            # 3. Resource Collection Phase
            print("\n3. Running Resource Collection...")
            # Extract use cases from the market analysis results
            use_cases_list = use_cases.split("\n")  # Assuming use cases are newline separated
            use_cases_list = [uc.strip() for uc in use_cases_list if uc.strip()]
            
            resource_agent = EnhancedResourceAssetAgent(use_cases=use_cases_list, industry=self.industry)
            resources = resource_agent.collect_resources(use_cases_list[0], self.industry)  # Pass first use case as example
            
            resource_file = os.path.join(self.output_dir, "collected_resources.json")
            resource_agent.save_resources(
                resources=resources,
                use_case=use_cases_list[0],
                markdown_content="# Resource Collection\n\n",
                output_dir=self.output_dir
            )
            print(f"Resources saved to: {resource_file}")
            
            # 4. Final Proposal Generation
            print("\n4. Generating Final Proposal...")
            proposal_file = os.path.join(self.proposals_dir, "final_proposal.json")
            generate_final_proposal_groq(
                research_file=research_file,
                market_file=market_file,
                resource_file=resource_file,
                output_file=proposal_file
            )
            print(f"Final proposal generated at: {proposal_file}")
            
            print("\nAI Implementation Analysis Complete!")
            
        except Exception as e:
            print(f"\nError during execution: {str(e)}")
            raise

if __name__ == "__main__":
    orchestrator = AIImplementationOrchestrator()
    orchestrator.run()