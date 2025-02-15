import streamlit as st
import json
from datetime import datetime
import os
from main import PressAgent
import base64

class StreamlitPressKit:
    def __init__(self):
        self.press_agent = PressAgent()

    def run(self):
        st.set_page_config(page_title="PressAgent - Press Kit Generator", layout="wide")
        
        # Header
        st.title("🚀 PressAgent - Professional Press Kit Generator")
        st.markdown("Generate comprehensive press kits with AI-powered content generation")

        # Sidebar for API keys
        with st.sidebar:
            st.header("API Configuration")
            huggingface_key = st.text_input("HuggingFace API Key", type="password")
            news_api_key = st.text_input("News API Key", type="password")
            
            if st.button("Save API Keys"):
                os.environ['HUGGINGFACE_API_KEY'] = huggingface_key
                os.environ['NEWS_API_KEY'] = news_api_key
                st.success("API keys saved!")

        # Main tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Information Collection", "Content Generation", "Quality Review", "Export"])

        # Tab 1: Information Collection
        with tab1:
            st.header("Company Information")
            
            # Company basic info
            col1, col2 = st.columns(2)
            with col1:
                company_name = st.text_input("Company Name")
                industry = st.text_input("Industry")
                year_founded = st.text_input("Year Founded")
                company_size = st.text_input("Company Size (e.g., 1-50, 51-200)")

            with col2:
                flagship_products = st.text_area("Flagship Products/Services (comma-separated)")
                achievements = st.text_area("Major Achievements (comma-separated)")
                brand_attributes = st.text_area("Brand Attributes (comma-separated)")

            # Press Release Details
            st.header("Press Release Details")
            col3, col4 = st.columns(2)
            with col3:
                topic = st.text_input("Press Release Topic")
                target_media = st.text_input("Target Media")
                target_audience = st.text_input("Target Audience")

            with col4:
                tone = st.selectbox("Tone", ["professional", "casual", "formal"])
                key_message = st.text_area("Key Message")
                call_to_action = st.text_input("Call to Action")

            if st.button("Collect News Articles"):
                if company_name:
                    with st.spinner("Collecting news articles..."):
                        supplementary_data = self.press_agent.data_collector.collect_supplementary_data(company_name)
                        if supplementary_data:
                            st.session_state['supplementary_data'] = supplementary_data
                            st.success("News articles collected successfully!")
                            
                            # Display collected articles
                            st.subheader("Collected News Articles")
                            for i, article in enumerate(supplementary_data['selected_news'], 1):
                                with st.expander(f"Article {i}: {article['title']}"):
                                    st.write(f"Source: {article['source']}")
                                    st.write(f"Published: {article['published_date']}")
                                    st.write(f"Description: {article['description']}")
                        else:
                            st.warning("No news articles found.")
                else:
                    st.error("Please enter company name first.")

        # Tab 2: Content Generation
        with tab2:
            if st.button("Generate Press Kit"):
                if 'company_info' not in st.session_state:
                    # Collect company info from inputs
                    company_info = {
                        'name': company_name,
                        'industry': industry,
                        'flagship_products': [x.strip() for x in flagship_products.split(',')],
                        'achievements': [x.strip() for x in achievements.split(',')],
                        'brand_attributes': [x.strip() for x in brand_attributes.split(',')],
                        'year_founded': year_founded,
                        'company_size': company_size,
                        'topic': topic,
                        'target_media': target_media,
                        'target_audience': target_audience,
                        'tone': tone,
                        'key_message': key_message,
                        'call_to_action': call_to_action
                    }
                    st.session_state['company_info'] = company_info

                with st.spinner("Generating press kit..."):
                    press_kit = self.press_agent.content_generator.generate_press_kit(
                        st.session_state['company_info'],
                        st.session_state.get('supplementary_data', None)
                    )
                    st.session_state['press_kit'] = press_kit
                    st.success("Press kit generated successfully!")

            if 'press_kit' in st.session_state:
                st.subheader("Generated Content")
                tabs = st.tabs(["Press Release", "Company Overview", "PR Message", "Email Draft"])
                
                with tabs[0]:
                    st.markdown(st.session_state['press_kit']['press_release'])
                with tabs[1]:
                    st.markdown(st.session_state['press_kit']['company_overview'])
                with tabs[2]:
                    st.markdown(st.session_state['press_kit']['pr_message'])
                with tabs[3]:
                    st.markdown(st.session_state['press_kit']['email_draft'])

        # Tab 3: Quality Review
        with tab3:
            if 'press_kit' in st.session_state:
                if st.button("Review Content"):
                    with st.spinner("Analyzing content quality..."):
                        review_result = self.press_agent.quality_reviewer.review_press_kit(st.session_state['press_kit'])
                        st.session_state['review_result'] = review_result
                        st.success("Content review completed!")

                if 'review_result' in st.session_state:
                    st.subheader("Quality Review Results")
                    
                    # Display overall score
                    st.metric("Overall Score", f"{st.session_state['review_result']['overall_score']:.1f}/10")
                    
                    # Display detailed scores
                    col5, col6 = st.columns(2)
                    with col5:
                        st.subheader("Detailed Scores")
                        for criterion, score in st.session_state['review_result']['scores'].items():
                            st.write(f"{criterion.replace('_', ' ').title()}: {score:.1f}/10")
                    
                    with col6:
                        st.subheader("Recommendations")
                        for rec in st.session_state['review_result']['recommendations']:
                            st.write(f"• {rec}")

        # Tab 4: Export
        with tab4:
            if 'press_kit' in st.session_state and 'review_result' in st.session_state:
                if st.button("Export Press Kit"):
                    try:
                        # Create timestamp and filename
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        company_name = st.session_state['company_info']['name'].replace(" ", "_")
                        
                        # Ensure output directory exists
                        os.makedirs('output', exist_ok=True)
                        
                        # Export files
                        base_filename = f"press_kit_{company_name}_{timestamp}"
                        
                        # Save JSON
                        json_path = f"output/{base_filename}.json"
                        with open(json_path, 'w', encoding='utf-8') as f:
                            json.dump({
                                'press_kit': st.session_state['press_kit'],
                                'review_result': st.session_state['review_result'],
                                'company_info': st.session_state['company_info']
                            }, f, ensure_ascii=False, indent=2)
                        
                        # Save Text
                        text_path = f"output/{base_filename}.txt"
                        with open(text_path, 'w', encoding='utf-8') as f:
                            f.write("=== PRESS KIT ===\n\n")
                            for section, content in st.session_state['press_kit'].items():
                                f.write(f"=== {section.upper()} ===\n")
                                f.write(content + "\n\n")
                        
                        st.success("Press kit exported successfully!")
                        
                        # Provide download buttons
                        with open(json_path, 'rb') as f:
                            json_data = f.read()
                            st.download_button(
                                label="Download JSON",
                                data=json_data,
                                file_name=f"{base_filename}.json",
                                mime="application/json"
                            )
                        
                        with open(text_path, 'rb') as f:
                            text_data = f.read()
                            st.download_button(
                                label="Download Text",
                                data=text_data,
                                file_name=f"{base_filename}.txt",
                                mime="text/plain"
                            )
                            
                    except Exception as e:
                        st.error(f"Error during export: {str(e)}")

if __name__ == "__main__":
    app = StreamlitPressKit()
    app.run()