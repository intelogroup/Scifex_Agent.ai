import streamlit as st
from anthropic import Anthropic
from datetime import datetime

class ScienceAnalysisAgent:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        
    def analyze_date(self):
        date = datetime.now()
        prompt = f"""Find 5 significant scientific discoveries from {date.strftime('%B %d')} throughout history.
        For each discovery, provide:
        - The year and discovery name
        - A simple child-friendly explanation
        - Current applications
        - Future prospects"""
        
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content

st.set_page_config(page_title="Daily Science Analysis")

st.title("🧬 Daily Science Analysis")
st.subheader(f"Discoveries from {datetime.now().strftime('%B %d')}")

api_key = st.text_input("Enter your Claude API key:", type="password")

if st.button("Analyze", type="primary"):
    if api_key:
        try:
            with st.spinner("Analyzing..."):
                agent = ScienceAnalysisAgent(api_key)
                analysis = agent.analyze_date()
                
                # Display results in clean cards
                for entry in analysis.split('\n\n'):
                    if entry.strip():
                        st.markdown("---")
                        st.markdown(entry)
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.error("Please enter your API key")
