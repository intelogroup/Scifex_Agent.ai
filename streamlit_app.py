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
        
    def safe_get(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
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
            sections = content.split('<h2>')
            for section in sections:
                if 'Events' in section or 'Science' in section:
                    lines = section.split('\n')
                    for line in lines:
                        if any(keyword in line.lower() for keyword in ['science', 'discovery', 'astronomy', 'invention', 'technology']):
                            year_match = re.search(r'\b\d{4}\b', line)
                            if year_match:
                                events.append({
                                    'source': 'Wikipedia',
                                    'url': url,
                                    'text': re.sub(r'<[^>]+>', '', line).strip(),
                                    'year': year_match.group()
                                })
        return events

    def scrape_britannica(self, date):
        formatted_date = date.strftime('%B-%d')
        url = f"https://www.britannica.com/on-this-day/{formatted_date}"
        content = self.safe_get(url)
        events = []
        if content:
            # Look for science-related events in the content
            matches = re.finditer(r'(\d{4})[^\n]*?(?:science|discovery|astronomy|physics|chemistry|biology|technology)', content.lower())
            for match in matches:
                events.append({
                    'source': 'Britannica',
                    'url': url,
                    'text': re.sub(r'<[^>]+>', '', match.group()).strip(),
                    'year': match.group(1)
                })
        return events

    def scrape_nasa(self, date):
        formatted_date = date.strftime('%Y/%m/%d')
        url = f"https://www.nasa.gov/news-release/{formatted_date}"
        content = self.safe_get(url)
        events = []
        if content:
            events.append({
                'source': 'NASA',
                'url': url,
                'text': "NASA Event found for this date",
                'year': date.strftime('%Y')
            })
        return events

    def scrape_facts_net(self, date):
        formatted_date = date.strftime('%B-%d')
        url = f"https://facts.net/history/historical-events/{formatted_date}"
        content = self.safe_get(url)
        events = []
        if content:
            # Look for science-related facts
            matches = re.finditer(r'(\d{4})[^\n]*?(?:science|discovery|invention|research)', content.lower())
            for match in matches:
                events.append({
                    'source': 'Facts.net',
                    'url': url,
                    'text': re.sub(r'<[^>]+>', '', match.group()).strip(),
                    'year': match.group(1)
                })
        return events

    def scrape_science_news(self, date):
        formatted_date = date.strftime('%Y/%m/%d')
        url = f"https://www.sciencenews.org/article/date/{formatted_date}"
        content = self.safe_get(url)
        events = []
        if content:
            # Extract science news articles
            article_matches = re.finditer(r'<article[^>]*>.*?</article>', content, re.DOTALL)
            for match in article_matches:
                article_content = match.group()
                events.append({
                    'source': 'Science News',
                    'url': url,
                    'text': re.sub(r'<[^>]+>', '', article_content[:200]).strip(),
                    'year': date.strftime('%Y')
                })
        return events

class ScienceAnalysisAgent:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.scraper = ScienceScraper()
        
    def analyze_date(self, selected_date):
        # Scrape facts from all sources in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.scraper.scrape_wikipedia, selected_date): "Wikipedia",
                executor.submit(self.scraper.scrape_britannica, selected_date): "Britannica",
                executor.submit(self.scraper.scrape_nasa, selected_date): "NASA",
                executor.submit(self.scraper.scrape_facts_net, selected_date): "Facts.net",
                executor.submit(self.scraper.scrape_science_news, selected_date): "Science News"
            }
            
            all_facts = []
            for future in futures:
                try:
                    facts = future.result()
                    if facts:
                        all_facts.extend(facts)
                except Exception as e:
                    st.warning(f"Failed to fetch from {futures[future]}: {str(e)}")
            
        if not all_facts:
            return None
            
        # Format facts for display with enhanced styling
        formatted_facts = []
        for i, fact in enumerate(all_facts, 1):
            formatted_facts.append(f"""
            <div class="fact-card">
                <div class="fact-header">
                    <span class="fact-number">#{i}</span>
                    <span class="fact-source">{fact['source']}</span>
                    <span class="fact-year">{fact['year']}</span>
                </div>
                <div class="fact-content">
                    <p class="fact-text">{fact['text']}</p>
                    <a href="{fact['url']}" target="_blank" class="fact-link">
                        <span class="link-text">View Source</span>
                        <span class="link-arrow">→</span>
                    </a>
                </div>
            </div>
            """)
            
        return "\n".join(formatted_facts)

# Streamlit UI with enhanced styling
st.set_page_config(page_title="SCIFEX - Science Facts", layout="centered")

st.markdown("""
<style>
    .fact-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #2196f3;
        transition: transform 0.2s;
    }
    .fact-card:hover {
        transform: translateY(-2px);
    }
    .fact-header {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }
    .fact-number {
        background: #2196f3;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
        margin-right: 10px;
    }
    .fact-source {
        color: #666;
        font-weight: 500;
        margin-right: 10px;
    }
    .fact-year {
        color: #888;
        font-size: 0.9em;
    }
    .fact-text {
        color: #333;
        line-height: 1.6;
        margin-bottom: 15px;
        font-size: 1.1em;
    }
    .fact-link {
        display: inline-flex;
        align-items: center;
        color: #2196f3;
        text-decoration: none;
        font-weight: 500;
        transition: color 0.2s;
    }
    .fact-link:hover {
        color: #1976d2;
    }
    .link-arrow {
        margin-left: 5px;
        transition: transform 0.2s;
    }
    .fact-link:hover .link-arrow {
        transform: translateX(3px);
    }
    .stButton button {
        background-color: #2196f3;
        color: white;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔬 SCIFEX - Scientific Facts Explorer")
st.markdown("Discover verified scientific events from multiple trusted sources")

col1, col2 = st.columns([2,1])
with col1:
    selected_date = st.date_input("Select Date", value=datetime.now())
with col2:
    api_key = st.text_input("Claude API Key", type="password")

if st.button("🔍 Explore Scientific Facts", type="primary", use_container_width=True):
    if api_key:
        try:
            with st.spinner("Searching multiple sources..."):
                agent = ScienceAnalysisAgent(api_key)
                facts = agent.analyze_date(selected_date)
                
                if facts:
                    st.markdown(facts, unsafe_allow_html=True)
                else:
                    st.info("No scientific facts found for this date. Try another date!")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.error("Please enter your API key.")
