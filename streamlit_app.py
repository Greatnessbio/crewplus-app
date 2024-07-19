import streamlit as st
import os
from praisonai import PraisonAI
from duckduckgo_search import DDGS
from praisonai_tools import BaseTool

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
            with st.spinner("Running PraisonAI... This may take a few minutes."):
                praisonai = PraisonAI(agent_yaml=agent_yaml)
                result = praisonai.run()
            st.subheader("Agent Output")
            st.write(result)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if st.checkbox("Show logs"):
    st.text_area("Logs", value="INFO:__main__:Current SQLite version: 3.46.0\nINFO:__main__:Using SQLite version: 3.46.0", height=300)
