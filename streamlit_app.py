import streamlit as st
from anthropic import Anthropic
from datetime import datetime

class ScienceAnalysisAgent:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-sonnet-20240229"
        
    def analyze_date(self):
        date = datetime.now()
        prompt = f"""Find 5 significant scientific discoveries that occurred on {date.strftime('%B %d')} throughout history. 
        Format your response as a list with 5 sections.
        For each section:
        Title: [Year] - [Discovery]
        Explanation: [Simple explanation for a child]
        Applications: [Current applications]
        Future: [Future prospects]"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content

def main():
    st.set_page_config(page_title="Daily Science Analysis", layout="wide")
    
    st.markdown("""
        <style>
        .stApp {
            background-color: #f8f9fa;
        }
        .discovery-card {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .section-title {
            color: #1e88e5;
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }
        .section-header {
            color: #333;
            font-size: 1.1em;
            font-weight: 600;
            margin-top: 15px;
            margin-bottom: 8px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🧬 Daily Science Analysis")
        st.markdown(f"### {datetime.now().strftime('%B %d')}")
        
        api_key = st.text_input("Enter your Claude API key:", type="password")
        
        if st.button("Discover Today's Science", type="primary", use_container_width=True):
            if api_key:
                with st.spinner("Analyzing historical scientific events..."):
                    try:
                        agent = ScienceAnalysisAgent(api_key)
                        content = agent.analyze_date()
                        
                        # Display each section in a card
                        sections = content.split('\n\n')
                        for section in sections:
                            if section.strip():
                                with st.container():
                                    st.markdown(
                                        f"""
                                        <div class="discovery-card">
                                            {section.replace('\n', '<br>')}
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.error("Please enter your API key")

if __name__ == "__main__":
    main()
