import streamlit as st
import os
import yaml
import traceback
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

# User inputs
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
        os.environ["OPENAI_API_KEY"] = openai_api_key

        # Construct agent_yaml from user inputs
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
            with st.spinner("Running PraisonAI... This may take a few minutes."):
                praisonai = PraisonAI(agent_yaml=agent_yaml)
                st.write("Agent created successfully. Starting execution...")
                result = praisonai.run()
                st.write("Agent execution completed.")
            
            st.subheader("Agent Output")
            if result:
                st.write(result)
            else:
                st.warning("The agent did not produce any output. This might be due to an error in execution or an issue with the configuration.")
                st.write("Debug Information:")
                st.write(f"Agent YAML:\n{agent_yaml}")
                st.write("Please check the logs for more information.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.write("Detailed error information:")
            st.code(traceback.format_exc())

if st.checkbox("Show logs"):
    st.text_area("Logs", value="INFO:__main__:Current SQLite version: 3.46.0\nINFO:__main__:Using SQLite version: 3.46.0", height=300)

# Add a section to display PraisonAI version
try:
    import praisonai
    st.sidebar.write(f"PraisonAI Version: {praisonai.__version__}")
except Exception as e:
    st.sidebar.write("Unable to determine PraisonAI version")
