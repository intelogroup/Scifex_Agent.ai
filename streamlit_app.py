import streamlit as st
from anthropic import Anthropic
from datetime import datetime

class ScienceAnalysisAgent:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        
    def fetch_facts(self, selected_date):
        formatted_date = selected_date.strftime('%B %d')
        
        prompt = f"""Find any scientific facts, events, births, or developments that occurred on {formatted_date} throughout history.
        Include ALL types of scientific events, not just major ones:
        - Scientific discoveries (any scale)
        - Scientists' birthdays or death anniversaries
        - Patent filings
        - Journal publications
        - Space events and observations
        - Medical advancements
        - Technology developments
        - Research publications
        - Laboratory achievements
        - Academic milestones
        
        Requirements:
        1. Include events of any significance level
        2. Include scientists' births and deaths
        3. Include both major and minor developments
        4. Include events from any time period
        5. If exact year is known, include it
        
        Format each fact as:
        ## 🔬 [Year if known] Scientific Fact
        **What Happened:** [clear description]
        **Field:** [area of science/technology]
        **Context:** [brief background]
        **Why Interesting:** [significance or impact]
        
        ---"""

        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            temperature=0.5,  # Increased to allow for more varied results
            messages=[{
                "role": "user", 
                "content": prompt
            }]
        )
        
        if hasattr(response, 'content'):
            return response.content
        return "Unable to retrieve scientific facts for this date."

st.set_page_config(page_title="SCIFEX - Daily Science Facts", layout="wide")

st.title("🔬 SCIFEX - Daily Science Facts")
st.subheader(f"Exploring Science History")

st.markdown("""
This tool finds any scientific facts or events for your chosen date, including:
- Discoveries and developments
- Scientists' birthdays
- Space events
- Technology milestones
- Research publications
- And more!
""")

col1, col2 = st.columns([2,1])
with col1:
    selected_date = st.date_input(
        "Select a date",
        value=datetime.now(),
        help="Choose any date to explore"
    )
with col2:
    api_key = st.text_input("Enter your Claude API key:", type="password")

if st.button("Find Facts", type="primary", use_container_width=True):
    if not api_key:
        st.error("Please enter your Claude API key.")
    else:
        try:
            with st.spinner("Finding scientific facts and events..."):
                agent = ScienceAnalysisAgent(api_key)
                results = agent.fetch_facts(selected_date)
                
                if "Scientific Fact" in results:
                    st.markdown(results)
                    st.success("Facts found! 🎉")
                else:
                    st.error("Error retrieving facts. Please try again.")
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

st.markdown("---")
st.caption("Explore the fascinating world of science, one day at a time! 🌟")
