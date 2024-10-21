import streamlit as st
from anthropic import Anthropic
from datetime import datetime

class ScienceAnalysisAgent:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        
    def analyze_date(self):
        date = datetime.now()
        prompt = """Analyze 5 significant scientific discoveries on this date. 
        For each discovery provide:
        TITLE: [year] - [discovery name]
        EXPLAIN: [child-friendly explanation]
        CURRENT: [current applications]
        FUTURE: [future prospects]
        
        Keep each section concise but informative."""
        
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content

st.set_page_config(page_title="Daily Science Analysis")

# Custom CSS for better formatting
st.markdown("""
    <style>
    .discovery-card {
        padding: 20px;
        border-radius: 5px;
        background-color: #f8f9fa;
        margin-bottom: 20px;
    }
    .section-title {
        color: #0066cc;
        font-weight: bold;
    }
    .section-content {
        margin-left: 20px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧬 Daily Science Analysis")
st.subheader(f"Discoveries from {datetime.now().strftime('%B %d')}")

api_key = st.text_input("Enter your Claude API key:", type="password")

if st.button("Analyze", type="primary"):
    if api_key:
        try:
            with st.spinner("Analyzing..."):
                agent = ScienceAnalysisAgent(api_key)
                analysis = agent.analyze_date()
                
                # Display each discovery in a formatted card
                discoveries = analysis.split('\n\n')  # Split by double newline if the response format allows
                for discovery in [analysis]:  # Use the whole response if splitting isn't possible
                    with st.container():
                        st.markdown("---")
                        st.markdown(f"""
                            <div class="discovery-card">
                                {discovery}
                            </div>
                            """, unsafe_allow_html=True)
                            
                        # Add expandable details section
                        with st.expander("💡 Learn More"):
                            st.markdown("Want to dive deeper into this discovery? Here's what you can explore:")
                            st.markdown("- 📚 Research papers and publications")
                            st.markdown("- 🔬 Related experiments and findings")
                            st.markdown("- 🎓 Educational resources")
                            
        except Exception as e:
            st.error(f"Error occurred: {str(e)}")
            st.error("Full error details:", exc_info=True)
    else:
        st.error("Please enter your API key")
