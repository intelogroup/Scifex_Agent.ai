import streamlit as st
from anthropic import Anthropic
from datetime import datetime

class ScienceAnalysisAgent:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        
    def analyze_date(self):
        date = datetime.now()
        prompt = """For exactly 5 scientific discoveries on this date, provide each in this exact format:
        TITLE: [year] - [discovery name]
        EXPLAIN: [child-friendly explanation]
        CURRENT: [current applications]
        FUTURE: [future prospects]
        ---"""
        
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
                
                # Display in cards using columns
                for i in range(5):
                    with st.container():
                        st.markdown("---")
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.markdown("### 🔬 Discovery")
                        with col2:
                            st.info(analysis[i])
        except Exception as e:
            st.error(f"Error occurred: {str(e)}")
    else:
        st.error("Please enter your API key")
