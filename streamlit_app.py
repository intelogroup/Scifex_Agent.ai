import streamlit as st
from anthropic import Anthropic
from datetime import datetime
import urllib.request
import json
from concurrent.futures import ThreadPoolExecutor
import re
from urllib.parse import urljoin, quote
import ssl

class ScienceScraper:
    def __init__(self):
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE
        
    def clean_text(self, text):
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        text = re.sub(r'\[\d+\]', '', text)
        return text

    def extract_year(self, text):
        current_year = datetime.now().year
        year_match = re.search(r'\b(1\d{3}|20[0-2]\d)\b', text)
        if year_match:
            year = int(year_match.group(1))
            if 1000 <= year <= current_year:
                return str(year)
        return None

    def safe_get(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml'
            }
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=self.ctx, timeout=10) as response:
                return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            return None

    def scrape_wikipedia(self, date):
        month_day = date.strftime('%B_%-d')
        url = f"https://en.wikipedia.org/wiki/{month_day}"
        content = self.safe_get(url)
        events = []
        
        if content:
            for line in content.split('\n'):
                if any(keyword in line.lower() for keyword in 
                      ['science', 'discovery', 'astronomy', 'physics', 'chemistry','astronomy','industry','nobel',
                       'biology', 'technology', 'invention', 'history','medicine','event','spacecraft', 'nasa']):
                    year = self.extract_year(line)
                    if year:
                        clean_text = self.clean_text(line)
                        event_text = re.sub(f'^{year}[^a-zA-Z]*', '', clean_text)
                        if event_text:
                            events.append({
                                'source': 'Wikipedia',
                                'url': url,
                                'text': event_text,
                                'year': year
                            })
        return events

    def scrape_britannica(self, date):
        formatted_date = date.strftime('%B-%d')
        url = f"https://www.britannica.com/on-this-day/{formatted_date}"
        
        content = self.safe_get(url)
        events = []
        
        if content:
            event_matches = re.finditer(r'(\d{4})[^\n]*?(?:science|discovery|astronomy|physics|chemistry|biology|technology|invention)', content.lower())
            for match in event_matches:
                text = match.group(0)
                year = self.extract_year(text)
                if year:
                    clean_text = self.clean_text(text)
                    events.append({
                        'source': 'Britannica',
                        'url': url,
                        'text': clean_text,
                        'year': year
                    })
        return events

class ScienceAnalysisAgent:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.scraper = ScienceScraper()
        
    def analyze_date(self, selected_date):
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(self.scraper.scrape_wikipedia, selected_date): "Wikipedia",
                executor.submit(self.scraper.scrape_britannica, selected_date): "Britannica"
            }
            
            all_facts = []
            for future in futures:
                try:
                    facts = future.result()
                    if facts:
                        all_facts.extend(facts)
                except Exception as e:
                    pass

        if not all_facts:
            return None

        all_facts.sort(key=lambda x: x['year'])
        
        formatted_facts = []
        for i, fact in enumerate(all_facts, 1):
            formatted_facts.append(f"""
            <div class="fact-card">
                <div class="fact-header">
                    <div class="fact-source-year">
                        <span class="fact-source">{fact['source']}</span>
                        <span class="fact-year">{fact['year']}</span>
                    </div>
                </div>
                <div class="fact-content">
                    <p class="fact-text">{fact['text']}</p>
                    <a href="{fact['url']}" target="_blank" class="fact-link">
                        Verify Source <span class="link-arrow">→</span>
                    </a>
                </div>
            </div>
            """)
        
        return "\n".join(formatted_facts)

st.set_page_config(page_title="SCIFEX - Science Facts", layout="centered")

st.markdown("""
<style>
    .fact-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #2196f3;
    }
    .fact-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    .fact-source-year {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .fact-source {
        background: #e3f2fd;
        color: #1976d2;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 500;
        font-size: 0.9em;
    }
    .fact-year {
        color: #666;
        font-weight: 500;
    }
    .fact-text {
        color: #333;
        line-height: 1.6;
        font-size: 1.1em;
        margin: 12px 0;
    }
    .fact-link {
        display: inline-flex;
        align-items: center;
        color: #2196f3;
        text-decoration: none;
        font-size: 0.9em;
        gap: 4px;
    }
    .link-arrow {
        transition: transform 0.2s;
    }
    .fact-link:hover .link-arrow {
        transform: translateX(4px);
    }
</style>
""", unsafe_allow_html=True)

st.title("🔬 SCIFEX - Scientific Facts Explorer")
st.markdown("Discover verified scientific events throughout history")

col1, col2 = st.columns([2,1])
with col1:
    selected_date = st.date_input("Select Date", value=datetime.now())
with col2:
    api_key = st.text_input("Claude API Key", type="password")

if st.button("🔍 Discover Facts", type="primary", use_container_width=True):
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
