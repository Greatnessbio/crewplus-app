import streamlit as st
import os
import yaml
import sys
import time
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_sqlite():
    try:
        import sqlite3
        logger.info(f"Current SQLite version: {sqlite3.sqlite_version}")
        if sqlite3.sqlite_version_info < (3, 35, 0):
            logger.info("SQLite version is older than 3.35.0. Attempting to use pysqlite3.")
            __import__('pysqlite3')
            sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
        logger.info(f"Using SQLite version: {sqlite3.sqlite_version}")
    except ImportError:
        logger.error("Failed to import pysqlite3. Please install it using: pip install pysqlite3-binary")
        st.error("There was an issue with the SQLite configuration. Please contact the app administrator.")
        st.stop()

setup_sqlite()

try:
    from praisonai import PraisonAI
    from duckduckgo_search import DDGS
    from praisonai_tools import BaseTool
except ImportError as e:
    logger.error(f"Failed to import required modules: {str(e)}")
    st.error(f"Failed to import required modules: {str(e)}")
    st.error("Please make sure all required packages are installed.")
    st.stop()

class InternetSearchTool(BaseTool):
    name: str = "InternetSearchTool"
    description: str = "Search Internet for relevant information based on a query or latest news"
    def _run(self, query: str):
        ddgs = DDGS()
        results = ddgs.text(keywords=query, region='wt-wt', safesearch='moderate', max_results=5)
        return results

# Template configurations
templates = {
    "Biotech Startup Funding": {
        "topic": "Biotech Startup Funding",
        "role_name": "biotech_analyst",
        "role_title": "Biotech Investment Researcher",
        "role_goal": "Identify and analyze recently funded biotech startups in {topic}",
        "role_backstory": "You are a sharp-eyed financial analyst specializing in the biotech sector, with a keen interest in tracking startup funding and company developments.",
        "task_name": "research_funded_startups",
        "task_description": "Investigate and compile information about biotech startups that have received significant funding in July 2024.",
        "task_expected_output": "A detailed report on recently funded biotech startups, including company names, funding amounts, investors, date funding received, contacts from about us page, and the startups' focus areas within biotechnology.",
        "tools": ["InternetSearchTool"]
    },
    "Space Exploration": {
        "topic": "Space Exploration",
        "role_name": "astronomer",
        "role_title": "Space Researcher",
        "role_goal": "Discover new insights about {topic}",
        "role_backstory": "You are a curious and dedicated astronomer with a passion for unraveling the mysteries of the cosmos.",
        "task_name": "investigate_exoplanets",
        "task_description": "Research and compile information about exoplanets discovered in the last decade.",
        "task_expected_output": "A summarized report on exoplanet discoveries, including their size, potential habitability, and distance from Earth.",
        "tools": ["InternetSearchTool"]
    },
    "Custom": {
        "topic": "",
        "role_name": "",
        "role_title": "",
        "role_goal": "",
        "role_backstory": "",
        "task_name": "",
        "task_description": "",
        "task_expected_output": "",
        "tools": []
    }
}

st.title("Universal PraisonAI Agent Creator")

# OpenAI API Key input
openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")

# Template selection
selected_template = st.selectbox("Select a template or create custom", list(templates.keys()))

# Agent Configuration
st.header("Agent Configuration")
framework = st.selectbox("Framework", ["crewai", "other_framework"])
topic = st.text_input("Topic", value=templates[selected_template]["topic"])

# Role Configuration
st.subheader("Role Configuration")
role_name = st.text_input("Role Name", value=templates[selected_template]["role_name"])
role_title = st.text_input("Role Title", value=templates[selected_template]["role_title"])
role_goal = st.text_area("Role Goal", value=templates[selected_template]["role_goal"])
role_backstory = st.text_area("Role Backstory", value=templates[selected_template]["role_backstory"])

# Task Configuration
st.subheader("Task Configuration")
task_name = st.text_input("Task Name", value=templates[selected_template]["task_name"])
task_description = st.text_area("Task Description", value=templates[selected_template]["task_description"])
task_expected_output = st.text_area("Expected Output", value=templates[selected_template]["task_expected_output"])

# Tool Selection
available_tools = ["InternetSearchTool"]
selected_tools = st.multiselect("Select Tools", available_tools, default=templates[selected_template]["tools"])

def run_agent_with_timeout(agent_yaml, timeout=300):
    def run_agent():
        praisonai = PraisonAI(agent_yaml=agent_yaml)
        return praisonai.run()

    with ThreadPoolExecutor() as executor:
        future = executor.submit(run_agent)
        try:
            return future.result(timeout=timeout)
        except TimeoutError:
            logger.error(f"Agent execution timed out after {timeout} seconds")
            raise TimeoutError(f"Agent execution timed out after {timeout} seconds")

if st.button("Generate Agent and Run"):
    if not openai_api_key:
        st.error("Please enter your OpenAI API Key")
    else:
        os.environ["OPENAI_API_KEY"] = openai_api_key
        
        agent_yaml = f"""
        framework: "{framework}"
        topic: "{topic}"
        roles:
          {role_name.lower().replace(" ", "_")}:
            role: "{role_title}"
            goal: "{role_goal}"
            backstory: "{role_backstory}"
            tasks:
              {task_name}:
                description: "{task_description}"
                expected_output: "{task_expected_output}"
            tools:
              {yaml.dump(selected_tools, default_flow_style=False)}
        """
        
        st.subheader("Generated YAML Configuration")
        st.code(agent_yaml, language="yaml")
        
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i in range(100):
                status_text.text(f"Running agent... {i+1}%")
                progress_bar.progress(i + 1)
                time.sleep(0.1)

            with st.spinner("Finalizing agent execution..."):
                result = run_agent_with_timeout(agent_yaml, timeout=300)  # 5-minute timeout
            
            st.success("Agent execution completed successfully!")
            st.subheader("Agent Output")
            st.markdown(result)
            
            # Download buttons
            st.download_button(
                label="Download YAML Configuration",
                data=agent_yaml,
                file_name="agent_configuration.yaml",
                mime="application/x-yaml"
            )
            
            st.download_button(
                label="Download Agent Output",
                data=result,
                file_name="agent_output.md",
                mime="text/markdown"
            )
        except TimeoutError:
            st.error("The agent execution timed out. Please try again with a simpler task or contact support.")
        except Exception as e:
            logger.error(f"An error occurred while running the agent: {str(e)}")
            st.error(f"An error occurred while running the agent: {str(e)}")
            st.error("If the error persists, please check your configuration and try again.")

st.sidebar.markdown("## About")
st.sidebar.markdown("This app allows you to create and run custom PraisonAI agents.")
st.sidebar.markdown("1. Enter your OpenAI API Key")
st.sidebar.markdown("2. Select a template or create a custom configuration")
st.sidebar.markdown("3. Modify the configuration as needed")
st.sidebar.markdown("4. Click 'Generate Agent and Run' to create and execute your agent")
st.sidebar.markdown("5. View the generated YAML configuration and agent output")
st.sidebar.markdown("6. Download the configuration and output as needed")

# Display logs in the Streamlit app
if st.checkbox("Show logs"):
    st.text_area("Logs", value="\n".join(logger.handlers[0].buffer), height=300)
