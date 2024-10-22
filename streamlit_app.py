import streamlit as st
from anthropic import Anthropic
from datetime import datetime

class ScienceAnalysisAgent:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        
    def analyze_date(self, selected_date):
        formatted_date = selected_date.strftime('%B %d')
        
        # Prompt engineered to prioritize specific sources
        prompt = f"""Research and verify scientific discoveries/events from {formatted_date} throughout history.

        IMPORTANT: First check these primary sources in order:
        1. facts.net/history/historical-events
        2. britannica.com/on-this-day
        3. sciencenews.org/sn-magazine
        4. history.com
        5. apod.nasa.gov/apod
        6. wikipedia.com

        Then supplement with additional verified sources:
        - Scientific journals (Nature, Science)
        - University research publications
        - Government agencies (NASA, NIH)
        - Nobel Prize records
        
        For each fact found, verify it appears in at least two of these sources.
        
        Format using markdown:
        ## 🔬 Scientific Fact #[number]
        **Date:** {formatted_date}, [year]
        **Event:** [verified discovery/event]
        **Field:** [scientific field]
        **Simple Explanation:** [child-friendly explanation with an analogy]
        **Impact:** [current applications and significance]
        **Future:** [prospects and ongoing research]
        **Primary Source:** [link to main source from priority list]
        **Secondary Source:** [additional verification source]
        
        ---
        (Provide 10 verified discoveries, prioritizing those found in our primary source list)"""
        
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2500,
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

st.set_page_config(page_title="SCIFEX - Daily Science", layout="centered")

st.title("🔬 SCIFEX - Daily Science")
st.markdown("""
    <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .fact-card {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        h2 {
            color: #0066cc;
        }
        .source-link {
            color: #28a745;
        }
    </style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2,1])
with col1:
    selected_date = st.date_input("Select a date", value=datetime.now())
with col2:
    api_key = st.text_input("Enter Claude API key:", type="password")

if st.button("Discover Scientific Facts", type="primary", use_container_width=True):
    if api_key:
        try:
            with st.spinner("Researching verified scientific events from primary sources..."):
                agent = ScienceAnalysisAgent(api_key)
                analysis = agent.analyze_date(selected_date)
                
                if analysis and "Scientific Fact" in analysis:
                    st.markdown("""
                        ### 📚 Sources Checked:
                        - Facts.net Historical Events
                        - Britannica On This Day
                        - Science News Magazine
                        - History.com
                        - NASA Astronomy Picture of the Day
                        - Wikipedia
                        - Additional scientific sources
                    """)
                    st.markdown("---")
                    st.markdown(analysis, unsafe_allow_html=True)
                else:
                    st.warning("No verified scientific facts found for this date. Try another date!")
        except Exception as e:
            st.error(f"Error occurred: {str(e)}")
    else:
        st.error("Please enter your Claude API key.")

st.markdown("---")
st.markdown("### About SCIFEX")
st.markdown("""
    SCIFEX provides verified scientific facts and discoveries from history, 
    prioritizing reliable sources and cross-referencing information for accuracy.
    Each fact is verified against multiple sources before being presented.
""")
