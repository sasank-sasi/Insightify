from tavily import TavilyClient
import json
import requests
from bs4 import BeautifulSoup
import os

class ResearchAgent:
    def __init__(self, api_key):
        self.client = TavilyClient(api_key=api_key)

    def search_company_info(self, company_name):
        try:
            query = f"What is {company_name}, and what are their main offerings and focus areas?"
            response = self.client.search(query)
            return response
        except Exception as e:
            return {"error": str(e)}
        
    def save_to_json(self, data, filename):
        try:
            output_dir = "/Users/sasanksasi/Downloads/project/intern/output"
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w') as file:
                json.dump(data, file, indent=4)
            print(f"Results saved to {filepath}")
        except Exception as e:
            print(f"Error saving to file: {e}")

    def scrape_company_website(self, company_url):
        try:
            # Make a request to the company website
            page = requests.get(company_url)
            soup = BeautifulSoup(page.content, 'html.parser')

            # Extract details like vision, product offerings, and strategic focus areas
            vision = self.extract_text_by_keywords(soup, ['vision', 'mission', 'about'])
            product_offerings = self.extract_text_by_keywords(soup, ['products', 'services', 'solutions'])
            focus_areas = self.extract_text_by_keywords(soup, ['focus areas', 'industries','strategy', 'priorities'])

            return {
                "vision": vision,
                "product_offerings": product_offerings,
                "focus_areas": focus_areas
            }

        except Exception as e:
            return {"error": f"Error scraping website: {str(e)}"}

    def extract_text_by_keywords(self, soup, keywords):
        # Try to find text matching the keywords in the website's paragraphs
        for keyword in keywords:
            # Look for sections containing the keyword
            sections = soup.find_all('p', string=lambda text: text and keyword.lower() in text.lower())
            if sections:
                return ' '.join([section.get_text() for section in sections])
        return "Information not found"

# Example Usage
if __name__ == "__main__":
    # Replace 'YOUR_API_KEY' with your actual Tavily API key.
    API_KEY = "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"
    research_agent = ResearchAgent(api_key=API_KEY)
    company_name = input("Enter the company name: ")
    research_results = research_agent.search_company_info(company_name)
    
    # Scrape additional data from the company website
    company_url = input("Enter the company URL to scrape: ")
    scraped_data = research_agent.scrape_company_website(company_url)
    
    # Combine research results and scraped data
    combined_data = {
        "research_results": research_results,
        "scraped_data": scraped_data
    }
    
    # Save combined data to JSON file
    filename = f"company_research.json"
    research_agent.save_to_json(combined_data, filename)
    print(f"Combined data saved to {filename}")