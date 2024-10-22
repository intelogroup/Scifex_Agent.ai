import streamlit as st
from anthropic import Anthropic
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import wikipedia
from scholarly import scholarly
import re

class ScienceAnalysisAgent:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.valid_domains = [
            '.edu', '.gov', 'nature.com', 'science.org', 'wikipedia.org',
            'sciencedirect.com', 'springer.com', 'nih.gov', 'nasa.gov'
        ]
        
    def verify_fact(self, year, event):
        """Verify fact against reliable sources"""
        search_query = f"{year} {event} {' OR '.join(self.valid_domains)}"
        
        try:
            # First check Wikipedia
            wiki_results = wikipedia.search(f"{year} {event}", results=1)
            if wiki_results:
                page = wikipedia.page(wiki_results[0], auto_suggest=False)
                if str(year) in page.content and any(keyword in page.content.lower() for keyword in ['science', 'discovery', 'invention', 'research']):
                    return True, page.url

            # Then check Google Scholar
            scholarly_results = scholarly.search_pubs(f"{year} {event}")
            first_result = next(scholarly_results, None)
            if first_result:
                return True, f"https://scholar.google.com/citations?view_op=view_citation&citation_for_view={first_result.id}"
                
        except Exception as e:
            st.warning(f"Verification warning: {str(e)}")
            
        return False, None

    def analyze_date(self, selected_date):
        formatted_date = selected_date.strftime('%B %d')
        
        # First prompt to get potential facts
        initial_prompt = f"""List 15 potentially significant scientific discoveries, breakthroughs, or publications that occurred on {formatted_date} throughout history.
        Focus only on well-documented events from:
        - Major scientific journals (Nature, Science, etc.)
        - University research announcements
        - Government agency reports (NASA, NIH, etc.)
        - Nobel Prize announcements
        - Patent publications
        - Peer-reviewed research publications
        
        Format as: [YEAR]: [EVENT]"""
        
        initial_response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[{"role": "user", "content": initial_prompt}]
        )
        
        # Extract and verify facts
        verified_facts = []
        potential_facts = initial_response.content
        
        for line in potential_facts.split('\n'):
            if ':' in line:
                year, event = line.split(':', 1)
                year = year.strip()
                event = event.strip()
                
                verified, source = self.verify_fact(year, event)
                if verified:
                    verified_facts.append((year, event, source))
                    if len(verified_facts) >= 10:
                        break
        
        # Generate detailed analysis for verified facts
        if verified_facts:
            analysis_prompt = f"""Analyze these verified scientific discoveries from {formatted_date}:
            {verified_facts}
            
            Format using markdown:
            ## 🔬 Verified Scientific Fact #{len(verified_facts)}
            **Year:** [year]
            **Event:** [discovery name]
            **Simple Explanation:** [child-friendly explanation]
            **Current Use:** [current applications]
            **Future:** [future prospects]
            **Source:** [source_url]
            
            Repeat for each fact."""
            
            final_response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1500,
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            
            return final_response.content
        else:
            return "No verified scientific facts found for this date. Try another date!"

# Rest of the Streamlit UI code remains the same...
