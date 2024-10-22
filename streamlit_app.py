import streamlit as st
from anthropic import Anthropic
from datetime import datetime

class ScienceAnalysisAgent:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        
    def analyze_date(self, selected_date):
        formatted_date = selected_date.strftime('%B %d')
        
        # Prompt engineered to request verified facts with sources
        prompt = f"""Analyze and provide 10 verified scientific discoveries/events from {formatted_date} throughout history.

        Important requirements:
        1. Only include facts that can be found in:
           - Major scientific journals (Nature, Science)
           - University research publications
           - Government agencies (NASA, NIH)
           - Nobel Prize records
           - Patent offices
           - Peer-reviewed publications
        
        2. For each fact, include:
           - The exact date and year
           - The scientific significance
           - A citation or reference
        
        Format using markdown:
        ## 🔬 Scientific Fact #[number]
        **Date:** {formatted_date}, [year]
        **Event:** [verified discovery/event]
        **Field:** [scientific field]
        **Simple Explanation:** [child-friendly explanation]
        **Impact:** [current applications]
        **Future:** [prospects and ongoing research]
        **Source:** [specific journal/institution/database reference]
        
        ---
        (Repeat format for up to 10 verified discoveries, prioritizing major scientific breakthroughs)"""
        
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
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

st.set_page_config(page_title="SCIFEX - Daily Science", layout="centered")

st.title("🔬 SCIFEX - Daily Science")
st.markdown("""
    <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
    </style>
""", unsafe_allow_html=True)

selected_date = st.date_input("Select a date", value=datetime.now())
api_key = st.text_input("Enter your Claude API key:", type="password")

if st.button("Discover Scientific Facts", type="primary"):
    if api_key:
        try:
            with st.spinner("Researching verified scientific events..."):
                agent = ScienceAnalysisAgent(api_key)
                analysis = agent.analyze_date(selected_date)
                
                if analysis and "Scientific Fact" in analysis:
                    st.markdown(analysis, unsafe_allow_html=True)
                else:
                    st.warning("No verified scientific facts found for this date. Try another date!")
        except Exception as e:
            st.error(f"Error occurred: {str(e)}")
    else:
        st.error("Please enter your Claude API key.")
