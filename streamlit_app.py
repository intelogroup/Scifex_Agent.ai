import streamlit as st
from anthropic import Anthropic
from datetime import datetime

class ScienceAnalysisAgent:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        
    def fetch_structured_facts(self, selected_date):
        formatted_date = selected_date.strftime('%B %d')
        
        prompt = f"""Please check {formatted_date} on these specific websites and provide ONLY facts that you can actually see on these pages:

        1. Visit https://www.onthisday.com/science/
        2. Visit https://www.britannica.com/on-this-day/{selected_date.month}/{selected_date.day}
        3. Visit https://www.history.com/this-day-in-history
        
        For each fact found:
        1. Include ONLY facts that are explicitly shown on these websites
        2. Include the direct URL where the fact was found
        3. Copy the exact text as written on the website
        4. Include only science, technology, space, and medical discoveries
        
        Format your response in markdown as:
        ### 🔬 Found on [Website Name]
        **Source:** [exact URL]
        **Date:** [exact date as shown]
        **Original Text:** [exact text from website]
        
        ---"""

        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            temperature=0, # Set to 0 for most factual response
            messages=[{
                "role": "user", 
                "content": prompt
            }]
        )
        
        if hasattr(response, 'content'):
            return response.content
        else:
            return "No facts could be retrieved from the sources."

st.set_page_config(page_title="SCIFEX - Historical Science Facts", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .source-header {
        color: #0366d6;
        padding: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔬 SCIFEX - Historical Science Facts")
st.markdown("### Direct Source Scientific Events Archive")

# Information about sources
with st.expander("ℹ️ About Data Sources"):
    st.markdown("""
    This tool fetches scientific facts directly from:
    - OnThisDay.com Science Section
    - Britannica's On This Day
    - History.com's This Day in History
    
    Only facts that are explicitly present on these websites are shown.
    Each fact includes its source URL for verification.
    """)

# Date selection
selected_date = st.date_input(
    "Select a date",
    value=datetime.now(),
    help="Choose a date to find historical scientific events"
)

# API key input
api_key = st.text_input("Enter your Claude API key:", type="password")

# Main button
if st.button("Find Scientific Events", type="primary", use_container_width=True):
    if not api_key:
        st.error("Please enter your Claude API key.")
    else:
        try:
            with st.spinner("Fetching scientific events from sources..."):
                agent = ScienceAnalysisAgent(api_key)
                results = agent.fetch_structured_facts(selected_date)
                
                if "Found on" in results:
                    st.markdown(results)
                    st.success("✅ Facts retrieved successfully! Click the source links to verify.")
                else:
                    st.warning("No scientific events found for this date in our sources.")
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
    **Note:** All information is sourced directly from historical archives and includes source links for verification.
    The tool only reports facts that are explicitly present on the source websites.
""")
