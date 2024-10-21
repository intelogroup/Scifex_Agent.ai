import streamlit as st
import anthropic
from datetime import datetime

class ScienceAnalysisAgent:
    def __init__(self, api_key: str):
        self.client = anthropic.Client(api_key=api_key)
        self.model = "claude-3-sonnet-20240229"
        
    def analyze_date(self):
        date = datetime.now()
        prompt = f"""Find 5 most significant scientific discoveries/events that occurred on {date.strftime('%B %d')} throughout history.
        For each discovery:
        1. Explain the science simply, as if to a child
        2. Describe current applications
        3. Outline future prospects"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content

st.set_page_config(page_title="Daily Science Analysis")
st.title("🧬 Daily Science Analysis")

api_key = st.text_input("Enter your Claude API key:", type="password")

if api_key and st.button("Get Today's Science Facts"):
    with st.spinner("Analyzing..."):
        try:
            agent = ScienceAnalysisAgent(api_key)
            analysis = agent.analyze_date()
            st.write(analysis)
        except Exception as e:
            st.error(f"Error: {str(e)}")
