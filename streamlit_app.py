import streamlit as st
from anthropic import Anthropic
from datetime import datetime

class ScienceAnalysisAgent:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        
    def fetch_facts(self, selected_date):
        formatted_date = selected_date.strftime('%B %d')
        
        prompt = f"""List any scientific facts and events from {formatted_date} (any year). Include:
        - Scientific discoveries
        - Scientists' birthdays
        - Inventions
        - Space events
        - Technology developments
        - Medical breakthroughs
        - Research milestones

        For each fact provide:
        1. The year
        2. What happened
        3. Brief explanation
        4. Why it matters

        Write in clear, simple language."""

        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                temperature=0.7,
                messages=[{
                    "role": "user", 
                    "content": prompt
                }]
            )
            
            return response.content if hasattr(response, 'content') else None
            
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return None

st.set_page_config(page_title="Daily Science Facts")

st.title("🔬 Daily Science Facts")
st.subheader("Discover what happened in science history")

selected_date = st.date_input("Select a date", value=datetime.now())
api_key = st.text_input("Enter your Claude API key:", type="password")

if st.button("Find Facts", type="primary"):
    if not api_key:
        st.error("Please enter your Claude API key.")
    else:
        try:
            with st.spinner("Searching..."):
                agent = ScienceAnalysisAgent(api_key)
                facts = agent.fetch_facts(selected_date)
                
                if facts:
                    st.markdown(facts)
                else:
                    st.warning("No facts found. Please try another date.")
                    
        except Exception as e:
            st.error(f"Error: {str(e)}")
