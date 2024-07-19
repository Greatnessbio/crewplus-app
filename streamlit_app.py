import streamlit as st
import os
import yaml
import logging
from praisonai import PraisonAI
from duckduckgo_search import DDGS
from praisonai_tools import BaseTool

# Set up logging
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

openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")

agent_yaml = """
framework: "crewai"
topic: "Biotech Startup Funding"
roles:
  biotech_analyst:
    role: "Biotech Investment Researcher"
    goal: "Identify and analyze recently funded biotech startups in {topic}"
    backstory: "You are a sharp-eyed financial analyst specializing in the biotech sector, with a keen interest in tracking startup funding and company developments."
    tasks:
      research_funded_startups:
        description: "Investigate and compile information about biotech startups that have received significant funding in July 2024."
        expected_output: "A detailed report on recently funded biotech startups, including company names, funding amounts, investors, date funding received, contacts from about us page, and the startups' focus areas within biotechnology."
    tools:
      - "InternetSearchTool"
"""

if st.button("Run PraisonAI"):
    if not openai_api_key:
        st.error("Please enter your OpenAI API Key")
    else:
        os.environ["OPENAI_API_KEY"] = openai_api_key
        try:
            logger.info("Creating PraisonAI instance")
            praisonai = PraisonAI(agent_yaml=agent_yaml)
            
            logger.info("Running PraisonAI agent")
            with st.spinner("Running PraisonAI... This may take a few minutes."):
                result = praisonai.run()
            
            logger.info("PraisonAI execution completed")
            st.subheader("Agent Output")
            if result:
                st.write(result)
            else:
                st.warning("The agent did not produce any output.")
                logger.warning("Agent produced no output")
            
            logger.info("Execution details:")
            logger.info(f"Agent YAML:\n{agent_yaml}")
            
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}", exc_info=True)
            st.error(f"An error occurred: {str(e)}")

if st.checkbox("Show logs"):
    log_output = st.empty()
    log_output.text_area("Logs", value=logger.handlers[0].stream.getvalue(), height=300)

# Display PraisonAI version
import praisonai
st.sidebar.write(f"PraisonAI Version: {praisonai.__version__}")
