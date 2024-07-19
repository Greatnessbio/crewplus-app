import streamlit as st
import os
import yaml
from praisonai import PraisonAI
from praisonai_tools import BaseTool
from duckduckgo_search import DDGS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InternetSearchTool(BaseTool):
    name: str = "InternetSearchTool"
    description: str = "Search Internet for relevant information based on a query or latest news"
    def _run(self, query: str):
        ddgs = DDGS()
        results = ddgs.text(keywords=query, region='wt-wt', safesearch='moderate', max_results=5)
        return results

st.title("PraisonAI Agent Creator")

# User inputs
openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")
topic = st.text_input("Topic", "Biotech Startup Funding")
role = st.text_input("Role", "Biotech Investment Researcher")
goal = st.text_area("Goal", "Identify and analyze recently funded biotech startups in {topic}")
backstory = st.text_area("Backstory", "You are a sharp-eyed financial analyst specializing in the biotech sector, with a keen interest in tracking startup funding and company developments.")
task_description = st.text_area("Task Description", "Investigate and compile information about biotech startups that have received significant funding in July 2024.")
expected_output = st.text_area("Expected Output", "A detailed report on recently funded biotech startups, including company names, funding amounts, investors, date funding received, contacts from about us page, and the startups' focus areas within biotechnology.")

if st.button("Run PraisonAI"):
    if not openai_api_key:
        st.error("Please enter your OpenAI API Key")
    else:
        # Set the API key
        os.environ["OPENAI_API_KEY"] = openai_api_key
        
        agent_yaml = f"""
        framework: "crewai"
        topic: "{topic}"
        roles:
          analyst:
            role: "{role}"
            goal: "{goal}"
            backstory: "{backstory}"
            tasks:
              research_task:
                description: "{task_description}"
                expected_output: "{expected_output}"
            tools:
              - "InternetSearchTool"
        """
        
        try:
            praisonai = PraisonAI(agent_yaml=agent_yaml)
            with st.spinner("Running PraisonAI... This may take a few minutes."):
                result = praisonai.run()
            
            if result:
                st.subheader("PraisonAI Output")
                st.write(result)
            else:
                st.error("PraisonAI returned no result. Please check the logs for more information.")
        except Exception as e:
            logger.error(f"An error occurred while running the agent: {str(e)}")
            st.error(f"An error occurred: {str(e)}")

# Display logs in the Streamlit app
if st.checkbox("Show logs"):
    st.text_area("Logs", value="\n".join(logger.handlers[0].buffer), height=300)

# Display PraisonAI version
import praisonai
st.sidebar.write(f"PraisonAI Version: {praisonai.__version__}")
