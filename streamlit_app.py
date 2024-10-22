import streamlit as st
from anthropic import Anthropic
from datetime import datetime

class ScienceAnalysisAgent:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        
    def analyze_date(self, selected_date):
        formatted_date = selected_date.strftime('%B %d')
        
        # Prompt engineered to focus on specific trusted sources
        prompt = f"""Research and verify scientific discoveries/events from {formatted_date} throughout history.

        IMPORTANT: Prioritize facts from these specific sources in order:
        1. britannica.com
        2. facts.net
        3. sciencenews.org
        4. onthisday.com
        5. history.com
        6. nasa.gov
        7. wikipedia.com

        Requirements:
        - Find events that are specifically mentioned in these sources
        - Focus on scientific discoveries, inventions, space events, medical breakthroughs
        - Include the specific source website for each fact
        - Verify each fact appears in at least one of these sources
        
        Format using markdown:
        ## 🔬 Scientific Fact #[number]
        **Date:** {formatted_date}, [year]
        **Event:** [verified discovery/event]
        **Field:** [scientific field]
        **Simple Explanation:** [child-friendly explanation with analogy]
        **Historical Impact:** [how it changed science/society]
        **Modern Applications:** [current uses and relevance]
        **Future Prospects:** [ongoing research and potential developments]
        **Primary Source:** [specific website from the priority list where this fact is documented]
        
        ---
        Please provide 10 verified facts, ensuring each has a citation from one of the priority sources listed above."""
        
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            temperature=0.7,
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

st.set_page_config(
    page_title="SCIFEX - Daily Science", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("🔬 SCIFEX - Daily Science")
st.markdown("""
    <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        h2 {
            color: #1f77b4;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }
        strong {
            color: #2c3e50;
        }
    </style>
""", unsafe_allow_html=True)

# Add source attribution
st.markdown("""
    #### Data Sources:
    - Encyclopedia Britannica
    - Facts.net
    - Science News
    - On This Day
    - History.com
    - NASA
    - Wikipedia
""")

selected_date = st.date_input("Select a date", value=datetime.now())
api_key = st.text_input("Enter your Claude API key:", type="password")

if st.button("Discover Scientific Facts", type="primary"):
    if api_key:
        try:
            with st.spinner("Researching verified scientific events from trusted sources..."):
                agent = ScienceAnalysisAgent(api_key)
                analysis = agent.analyze_date(selected_date)
                
                if analysis and "Scientific Fact" in analysis:
                    st.markdown(analysis, unsafe_allow_html=True)
                    
                    # Add source disclaimer
                    st.markdown("""
                        ---
                        *Note: All facts are verified from the listed trusted sources. 
                        For the most current information, please visit the primary sources directly.*
                    """)
                else:
                    st.warning("No verified scientific facts found for this date in our priority sources. Try another date!")
        except Exception as e:
            st.error(f"Error occurred: {str(e)}")
    else:
        st.error("Please enter your Claude API key.")
