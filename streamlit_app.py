import streamlit as st
import os
import yaml
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

st.title("Universal PraisonAI Agent Creator")

# OpenAI API Key input
openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")

# Agent Configuration
st.header("Agent Configuration")
framework = st.selectbox("Framework", ["crewai", "other_framework"])  # Add more frameworks as needed
topic = st.text_input("Topic", "Custom Agent Topic")

# Role Configuration
st.subheader("Role Configuration")
role_name = st.text_input("Role Name", "Custom Role")
role_title = st.text_input("Role Title", "Custom Role Title")
role_goal = st.text_area("Role Goal", "Define the goal for this role")
role_backstory = st.text_area("Role Backstory", "Provide a backstory for this role")

# Task Configuration
st.subheader("Task Configuration")
task_name = st.text_input("Task Name", "custom_task")
task_description = st.text_area("Task Description", "Describe the task to be performed")
task_expected_output = st.text_area("Expected Output", "Describe the expected output of the task")

# Tool Selection
available_tools = ["InternetSearchTool"]  # Add more tools as they become available
selected_tools = st.multiselect("Select Tools", available_tools)

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
        
        with st.spinner("Running agent... This may take a few minutes."):
            try:
                praisonai = PraisonAI(agent_yaml=agent_yaml)
                result = praisonai.run()
                
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
            except Exception as e:
                st.error(f"An error occurred while running the agent: {str(e)}")

st.sidebar.markdown("## About")
st.sidebar.markdown("This app allows you to create and run custom PraisonAI agents.")
st.sidebar.markdown("1. Enter your OpenAI API Key")
st.sidebar.markdown("2. Configure your agent by filling out the forms")
st.sidebar.markdown("3. Click 'Generate Agent and Run' to create and execute your custom agent")
st.sidebar.markdown("4. View the generated YAML configuration and agent output")
st.sidebar.markdown("5. Download the configuration and output as needed")
