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

# User inputs (same as before)
...

if st.button("Run PraisonAI"):
    if not openai_api_key:
        st.error("Please enter your OpenAI API Key")
    else:
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
