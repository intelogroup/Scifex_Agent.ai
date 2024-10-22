import streamlit as st
from anthropic import Anthropic
from datetime import datetime

class ScienceAnalysisAgent:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        
    def fetch_facts(self, selected_date):
        formatted_date = selected_date.strftime('%B %d')
        
        prompt = f"""Based on your knowledge, provide verified scientific events, discoveries, and breakthroughs that occurred on {formatted_date} throughout history.

        Requirements:
        1. Only include events that you are highly confident about
        2. Focus on major scientific breakthroughs, space events, medical discoveries, and technological innovations
        3. Include the exact year and a reference if possible
        4. Skip social or political events unless they have major scientific impact
        5. Only include events you can cite with a specific source

        Format as:
        ## Scientific Event [Year]
        **Event:** [description]
        **Field:** [area of science]
        **Significance:** [why it matters]
        **Reference:** [source where this can be verified]

        ---"""

        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            temperature=0.1,
            messages=[{
                "role": "user", 
                "content": prompt
            }]
        )
        
        if hasattr(response, 'content'):
            return response.content
        return "No verified scientific events found for this date."

st.set_page_config(page_title="SCIFEX - Scientific History", layout="wide")

st.title("🔬 SCIFEX - Scientific History")

st.info("""
This tool provides information about historical scientific events based on verified sources. 
Each fact includes references where possible for further reading and verification.
""")

selected_date = st.date_input(
    "Select a date",
    value=datetime.now(),
    help="Choose a date to explore scientific history"
)

api_key = st.text_input("Enter your Claude API key:", type="password")

if st.button("Discover Scientific Events", type="primary"):
    if not api_key:
        st.error("Please enter your Claude API key.")
    else:
        try:
            with st.spinner("Researching scientific events..."):
                agent = ScienceAnalysisAgent(api_key)
                results = agent.fetch_facts(selected_date)
                
                if "Scientific Event" in results:
                    st.markdown(results)
                    st.markdown("---")
                    st.info("📚 Click the references to learn more about each event.")
                else:
                    st.warning("""
                    No major scientific events found for this specific date. 
                    Try another date or broaden the search criteria.
                    """)
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.caption("""
Note: This tool uses Claude's knowledge base to find verified scientific events. 
While we strive for accuracy, always cross-reference with primary sources for research purposes.
""")
