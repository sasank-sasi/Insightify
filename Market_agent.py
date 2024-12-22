import os
import json
from tavily import TavilyClient
from groq import Groq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from dotenv import load_dotenv

class UseCaseAgent:
    def __init__(self, api_key, groq_key):
        self.client = TavilyClient(api_key=api_key)
        self.groq_client = Groq(api_key=groq_key)

    def analyze_trends(self, industry):
        try:
            query = f"What are the latest AI and ML trends in the {industry} industry?"
            response = self.client.search(query)
            return response
        except Exception as e:
            return {"error": f"Error analyzing trends: {str(e)}"}

    def generate_use_cases(self, industry):
        try:
            prompt = (
                f"Suggest five innovative use cases where a company in the {industry} industry can use "
                "Generative AI, Large Language Models, and Machine Learning to improve operational efficiency, "
                "enhance customer satisfaction, and optimize resources."
            )
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama3-8b-8192",
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return {"error": f"Error generating use cases: {str(e)}"}
        
    def save_to_json(data, filename):
        try:
            output_dir = "/Users/sasanksasi/Downloads/project/intern/output"
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w') as file:
                json.dump(data, file, indent=4)
            print(f"Results saved to {filepath}")
        except Exception as e:
            print(f"Error saving to file: {e}")
        
    def save_to_markdown(self, data, filename):
        try:
            self.output_dir = "/Users/sasanksasi/Downloads/project/intern/output"
            os.makedirs(self.output_dir, exist_ok=True)
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w') as file:
                file.write(data)
            print(f"Results saved to {filepath}")
        except Exception as e:
            print(f"Error saving to file: {e}")

    def save_to_json(self, data, filename):
        try:
            self.output_dir = "/Users/sasanksasi/Downloads/project/intern/output"
            os.makedirs(self.output_dir, exist_ok=True)
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w') as file:
                json.dump(data, file, indent=4)
            print(f"Results saved to {filepath}")
        except Exception as e:
            print(f"Error saving to file: {e}")
        
        

# Example usage
if __name__ == "__main__":
    load_dotenv()  # Load variables from .env file

    API_KEY = os.getenv("TAVILY_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    if not API_KEY or not GROQ_API_KEY:
        print("API key(s) missing. Please set the TAVILY_API_KEY and GROQ_API_KEY environment variables.")
        exit()

    agent = UseCaseAgent(api_key=API_KEY, groq_key=GROQ_API_KEY)
    industry = input("Enter the industry: ")

    # Analyze trends
    trends = agent.analyze_trends(industry)

    # Generate use cases
    use_cases = agent.generate_use_cases(industry)
    print("Use Cases:", use_cases)

    # Combine results
    results = {
        "trends": trends,
        "use_cases": use_cases
    }
    
    res = {
        "use_cases": use_cases
    }

    # Save results to JSON file
    agent.save_to_json(results, "market_analysis.json")
    agent.save_to_json(res, "use_cases.json")
    # Save results to Markdown file
    markdown_content = f"# Use Cases for {industry}\n\n"

    markdown_content += f"## Use Cases\n\n{use_cases}\n"
    agent.save_to_markdown(markdown_content, "use_cases.md")
    
    print("Market Analysis Results saved successfully.")