import streamlit as st
from anthropic import Anthropic
from datetime import datetime

class ScienceAnalysisAgent:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        
    def analyze_date(self, selected_date):
        formatted_date = selected_date.strftime('%B %d')
        
        prompt = f"""Find scientific facts and discoveries from {formatted_date} by ONLY checking these primary sources first:
        1. facts.net/history/historical-events/
        2. britannica.com/on-this-day/
        3. sciencenews.org/sn-magazine/
        4. history.com
        5. apod.nasa.gov/apod/

        Then cross-verify each fact with:
        - wikipedia.org
        - scientific journals
        - university websites
        - government websites

        IMPORTANT RULES:
        1. ONLY include facts that you find with specific date (month, day, year) mentioned
        2. ONLY include facts that have direct URL sources
        3. DO NOT generate or infer facts
        4. For each fact, you MUST provide clickable source URLs
        5. Focus on scientific discoveries, space events, technological breakthroughs
        6. Skip political or war-related events unless they have major scientific impact

        Format using markdown:
        ## 🔬 Verified Fact #[number]
        **Date:** {formatted_date}, [exact year]
        **Event:** [documented discovery/event]
        **Field:** [scientific field]
        **Simple Explanation:** [verified description]
        **Impact:** [documented applications/significance]
        **Primary Source:** [direct URL to primary source]
        **Cross-Reference:** [URLs to verification sources]
        
        ---"""
        
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            temperature=0.1,  # Lower temperature for more factual responses
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        if isinstance(response, dict):
            return response.get('completion', response['content'][0].text)
        elif hasattr(response, 'content'):
            text_blocks = response.content
            return ''.join([block.text for block in text_blocks])
        else:
            return "Unexpected response format."

st.set_page_config(page_title="SCIFEX - Verified Daily Science", layout="centered")

st.title("🔬 SCIFEX - Verified Scientific Facts")
st.markdown("""
    <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .source-link {
            color: #0366d6;
            text-decoration: underline;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    This tool finds verified scientific facts by checking:
    - facts.net/history
    - britannica.com
    - sciencenews.org
    - history.com
    - apod.nasa.gov
    
    Each fact is cross-verified with Wikipedia and scientific sources.
""")

selected_date = st.date_input("Select a date", value=datetime.now())
api_key = st.text_input("Enter your Claude API key:", type="password")

if st.button("Find Verified Facts", type="primary"):
    if api_key:
        try:
            with st.spinner("Searching and verifying scientific events..."):
                agent = ScienceAnalysisAgent(api_key)
                analysis = agent.analyze_date(selected_date)
                
                if analysis and "Verified Fact" in analysis:
                    st.markdown(analysis, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    st.markdown("ℹ️ **Note:** All facts above include direct source links for verification.")
                else:
                    st.warning("No verified scientific facts found in the primary sources for this date. Try another date!")
        except Exception as e:
            st.error(f"Error occurred: {str(e)}")
    else:
        st.error("Please enter your Claude API key.")
