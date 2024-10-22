import streamlit as st
from anthropic import Anthropic
from datetime import datetime
import urllib.request
import json
from concurrent.futures import ThreadPoolExecutor
import re
from urllib.parse import urljoin
import ssl

class ScienceScraper:
    def __init__(self):
        # Bypass SSL verification for some sites
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE
        
    def safe_get(self, url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=self.ctx, timeout=10) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            return None

    def scrape_wikipedia(self, date):
        month_day = date.strftime('%B_%-d')
        url = f"https://en.wikipedia.org/wiki/{month_day}"
        content = self.safe_get(url)
        if content:
            # Extract science/technology related events
            events = []
            for line in content.split('\n'):
                if 'science' in line.lower() or 'discovery' in line.lower() or 'astronomy' in line.lower():
                    if re.search(r'\d{4}', line):  # Has a year
                        events.append({
                            'source': 'Wikipedia',
                            'url': url,
                            'text': line.strip(),
                            'year': re.search(r'\d{4}', line).group()
                        })
            return events
        return []

    def scrape_nasa_apod(self, date):
        formatted_date = date.strftime('%y%m%d')
        url = f"https://apod.nasa.gov/apod/ap{formatted_date}.html"
        content = self.safe_get(url)
        if content:
            return [{
                'source': 'NASA APOD',
                'url': url,
                'text': content[:500],  # Get first 500 chars
                'year': date.strftime('%Y')
            }]
        return []

class ScienceAnalysisAgent:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.scraper = ScienceScraper()
        
    def analyze_date(self, selected_date):
        # Scrape facts from multiple sources
        with ThreadPoolExecutor() as executor:
            wiki_future = executor.submit(self.scraper.scrape_wikipedia, selected_date)
            nasa_future = executor.submit(self.scraper.scrape_nasa_apod, selected_date)
            
            all_facts = []
            all_facts.extend(wiki_future.result())
            all_facts.extend(nasa_future.result())
            
        if not all_facts:
            return None
            
        # Format facts for display
        formatted_facts = []
        for i, fact in enumerate(all_facts, 1):
            formatted_facts.append(f"""
            <div class="fact-card">
                <div class="fact-number">Fact #{i}</div>
                <div class="fact-content">
                    <div class="fact-source">{fact['source']} ({fact['year']})</div>
                    <div class="fact-text">{fact['text']}</div>
                    <a href="{fact['url']}" target="_blank" class="fact-link">View Source →</a>
                </div>
            </div>
            """)
            
        return "\n".join(formatted_facts)

# Streamlit UI
st.set_page_config(page_title="SCIFEX - Science Facts", layout="centered")

# Custom CSS
st.markdown("""
<style>
    .fact-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 5px solid #1e88e5;
    }
    .fact-number {
        color: #1e88e5;
        font-weight: bold;
        font-size: 1.2em;
        margin-bottom: 10px;
    }
    .fact-source {
        color: #666;
        font-size: 0.9em;
        margin-bottom: 8px;
    }
    .fact-text {
        color: #333;
        line-height: 1.6;
        margin-bottom: 15px;
    }
    .fact-link {
        display: inline-block;
        color: #1e88e5;
        text-decoration: none;
        font-size: 0.9em;
        transition: color 0.2s;
    }
    .fact-link:hover {
        color: #1565c0;
    }
    .main-title {
        text-align: center;
        color: #1e88e5;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">🔬 SCIFEX - Daily Science Facts</h1>', unsafe_allow_html=True)

col1, col2 = st.columns([2,1])
with col1:
    selected_date = st.date_input("Select Date", value=datetime.now())
with col2:
    api_key = st.text_input("Claude API Key", type="password")

if st.button("🔍 Find Scientific Facts", type="primary", use_container_width=True):
    if api_key:
        try:
            with st.spinner("Searching verified sources..."):
                agent = ScienceAnalysisAgent(api_key)
                facts = agent.analyze_date(selected_date)
                
                if facts:
                    st.markdown(facts, unsafe_allow_html=True)
                else:
                    st.info("No verified scientific facts found for this date. Try another date!")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.error("Please enter your API key.")
