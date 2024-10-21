import streamlit as st
from anthropic import Anthropic
from datetime import datetime
import re

class ScienceAnalysisAgent:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-sonnet-20240229"
        
    def parse_response(self, response_content):
        discoveries = []
        lines = response_content.split('\n')
        current_discovery = None
        
        for line in lines:
            if re.match(r'^\d+\.', line):
                if current_discovery:
                    discoveries.append(current_discovery)
                current_discovery = {
                    'title': line.strip(),
                    'explanation': '',
                    'applications': '',
                    'prospects': ''
                }
            elif current_discovery:
                if 'a. Explanation:' in line:
                    current_discovery['explanation'] = line.replace('a. Explanation:', '').strip()
                elif 'b. Current Applications:' in line:
                    current_discovery['applications'] = line.replace('b. Current Applications:', '').strip()
                elif 'c. Future Prospects:' in line:
                    current_discovery['prospects'] = line.replace('c. Future Prospects:', '').strip()
        
        if current_discovery:
            discoveries.append(current_discovery)
        
        return discoveries

    def analyze_date(self):
        date = datetime.now()
        prompt = f"""Find 5 most significant scientific discoveries/events that occurred on {date.strftime('%B %d')} throughout history.
        For each discovery, provide:
        1. The title and year
        2. a. Explanation: A simple explanation a child would understand
        3. b. Current Applications: Current practical uses
        4. c. Future Prospects: Future potential developments"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        return self.parse_response(response.content)

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
        .card-title {
            color: #1e88e5;
            font-size: 1.4em;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .section-header {
            color: #333;
            font-size: 1.1em;
            font-weight: 600;
            margin: 15px 0 8px 0;
        }
        .section-content {
            color: #555;
            line-height: 1.6;
            margin-bottom: 12px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🧬 Daily Science Analysis")
        st.markdown(f"### Discoveries on {datetime.now().strftime('%B %d')}")
        
        api_key = st.text_input("Enter your Claude API key:", type="password")
        
        if st.button("Discover Today's Science", type="primary", use_container_width=True):
            if api_key:
                with st.spinner("Analyzing scientific events..."):
                    try:
                        agent = ScienceAnalysisAgent(api_key)
                        discoveries = agent.analyze_date()
                        
                        for discovery in discoveries:
                            st.markdown(f"""
                                <div class="discovery-card">
                                    <div class="card-title">{discovery['title']}</div>
                                    
                                    <div class="section-header">🔬 Simple Explanation</div>
                                    <div class="section-content">{discovery['explanation']}</div>
                                    
                                    <div class="section-header">🚀 Current Applications</div>
                                    <div class="section-content">{discovery['applications']}</div>
                                    
                                    <div class="section-header">🔮 Future Prospects</div>
                                    <div class="section-content">{discovery['prospects']}</div>
                                </div>
                            """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.error("Please enter your API key")

if __name__ == "__main__":
    main()
