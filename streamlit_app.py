import streamlit as st
from anthropic import Anthropic
from datetime import datetime
import re

class ScienceAnalysisAgent:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-sonnet-20240229"
        
    def parse_response(self, text):
        discoveries = []
        current_discovery = {}
        
        # Split the text into sections for each discovery
        sections = text.split("\n\n")
        
        for section in sections:
            if re.match(r'^\d+\.', section):  # New discovery
                if current_discovery:
                    discoveries.append(current_discovery)
                current_discovery = {'text': section.split('\n')[0]}
                
                # Extract explanations
                explanation = re.search(r'a\. Explanation: (.*?)(?=\n|$)', section)
                applications = re.search(r'b\. Current Applications: (.*?)(?=\n|$)', section)
                prospects = re.search(r'c\. Future Prospects: (.*?)(?=\n|$)', section)
                
                if explanation:
                    current_discovery['explanation'] = explanation.group(1)
                if applications:
                    current_discovery['applications'] = applications.group(1)
                if prospects:
                    current_discovery['prospects'] = prospects.group(1)
                    
        if current_discovery:
            discoveries.append(current_discovery)
            
        return discoveries

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
        return self.parse_response(response.content)

def main():
    st.set_page_config(page_title="Daily Science Analysis", layout="wide")
    
    # Custom CSS
    st.markdown("""
        <style>
        .stApp {
            background-color: #f8f9fa;
        }
        .discovery-card {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .section-header {
            color: #1f77b4;
            font-size: 1.2em;
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("🧬 Daily Science Analysis")
    st.markdown(f"### Scientific Discoveries on {datetime.now().strftime('%B %d')}")
    
    # Input
    col1, col2 = st.columns([3, 1])
    with col1:
        api_key = st.text_input("Enter your Claude API key:", type="password")
    with col2:
        analyze_button = st.button("Analyze", type="primary")
    
    if api_key and analyze_button:
        with st.spinner("Analyzing scientific events..."):
            try:
                agent = ScienceAnalysisAgent(api_key)
                discoveries = agent.analyze_date()
                
                for i, discovery in enumerate(discoveries, 1):
                    st.markdown(f"""
                        <div class="discovery-card">
                            <h3>{discovery['text']}</h3>
                            <div class="section-header">🔬 Simple Explanation</div>
                            <p>{discovery.get('explanation', '')}</p>
                            <div class="section-header">🚀 Current Applications</div>
                            <p>{discovery.get('applications', '')}</p>
                            <div class="section-header">🔮 Future Prospects</div>
                            <p>{discovery.get('prospects', '')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
