import os
import json
from groq import Groq
from dotenv import load_dotenv
from typing import Dict, Any
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def load_json(file_path: str) -> Dict:
    """Load JSON content from a file."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"File not found: {file_path}")

def extract_with_groq(client: Groq, data: Dict, prompt: str) -> str:
    """Extract insights using Groq chat completion."""
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a business analyst specialized in AI implementation strategies."},
                {"role": "user", "content": prompt}
            ],
            model="mixtral-8x7b-32768",
            temperature=0.3,
            max_tokens=800
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error in Groq extraction: {str(e)}"

def generate_pdf(proposal: Dict, output_path: str) -> None:
    """Generate PDF using reportlab."""
    try:
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12
        )
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=12
        )

        content = []
        content.append(Paragraph("AI Implementation Proposal", title_style))
        content.append(Spacer(1, 12))

        content.append(Paragraph("Company Overview", heading_style))
        content.append(Paragraph(proposal['Company Overview'], body_style))
        content.append(Spacer(1, 12))

        content.append(Paragraph("Industry Insights", heading_style))
        content.append(Paragraph(proposal['Industry Insights'], body_style))
        content.append(Spacer(1, 12))

        content.append(Paragraph("Proposed Use Cases", heading_style))
        content.append(Paragraph(proposal['Proposed Use Cases'], body_style))
        content.append(Spacer(1, 12))

        content.append(Paragraph("Resource Links", heading_style))
        for resource in proposal['Resource Links']:
            if isinstance(resource, dict):
                text = f"• {resource.get('source', 'N/A')}: {resource.get('url', 'N/A')}"
            else:
                text = f"• {resource}"
            content.append(Paragraph(text, body_style))

        doc.build(content)
        print(f"PDF generated successfully: {output_path}")

    except Exception as e:
        print(f"Error generating PDF: {str(e)}")

def generate_final_proposal_groq(research_file: str, market_file: str, resource_file: str, output_file: str) -> None:
    """Generate final proposal using Groq."""
    load_dotenv()
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    try:
        # Load inputs
        research_data = load_json(research_file)
        market_data = load_json(market_file)
        resource_data = load_json(resource_file)
        
        # Enhanced prompts
        company_prompt = f"""
        Analyze this company data and provide:
        1. Core business overview
        2. Current capabilities
        3. Key strengths and challenges
        4. Strategic priorities
        Data: {json.dumps(research_data)}
        """

        industry_prompt = f"""
        Extract key industry insights including:
        1. Market trends
        2. Technology adoption patterns
        3. Competitive landscape
        4. Growth opportunities
        Data: {json.dumps(market_data)}
        """

        use_cases_prompt = f"""
        Identify and prioritize use cases:
        1. Top 3-5 high-impact opportunities
        2. Implementation complexity
        3. Expected benefits
        4. Required capabilities
        Data: {json.dumps(market_data)}
        """
        
        # Generate insights
        company_info = extract_with_groq(groq_client, research_data, company_prompt)
        industry_info = extract_with_groq(groq_client, market_data, industry_prompt)
        proposed_use_cases = extract_with_groq(groq_client, market_data, use_cases_prompt)
        
        final_proposal = {
            "Company Overview": company_info,
            "Industry Insights": industry_info,
            "Proposed Use Cases": proposed_use_cases,
            "Resource Links": resource_data
        }

        # Save JSON
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(final_proposal, f, indent=4)

        # Generate and save PDF
        pdf_path = output_file.replace('.json', '.pdf')
        generate_pdf(final_proposal, pdf_path)

        print(f"Enhanced final proposal saved to:")
        print(f"JSON: {output_file}")
        print(f"PDF: {pdf_path}")

    except Exception as e:
        print(f"Error generating proposal: {str(e)}")

if __name__ == "__main__":
    research_json_path = "output/company_research.json"
    market_json_path = "output/market_analysis.json"
    resource_json_path = "output/collected_resources.json"
    final_output_path = "proposals/final_proposal.json"

    generate_final_proposal_groq(
        research_file=research_json_path,
        market_file=market_json_path,
        resource_file=resource_json_path,
        output_file=final_output_path
    )