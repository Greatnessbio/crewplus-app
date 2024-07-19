import streamlit as st
import yaml
import os
from praisonai import PraisonAI

st.title("PraisonAI Agent Creator")

# OpenAI API Key input
openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")
if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key

# Template selection
selected_template = st.selectbox("Select a template or create custom", ["Biotech Startup Funding"])

# Agent Configuration
st.header("Agent Configuration")
framework = st.selectbox("Framework", ["crewai"])
topic = st.text_input("Topic", value="Biotech Startup Funding")

# Role Configuration
st.header("Role Configuration")
role_name = st.text_input("Role Name", value="biotech_analyst")
role_title = st.text_input("Role Title", value="Biotech Investment Researcher")
role_goal = st.text_area("Role Goal", value="Identify and analyze recently funded biotech startups in {topic}")
role_backstory = st.text_area("Role Backstory", value="You are a sharp-eyed financial analyst specializing in the biotech sector, with a keen interest in tracking startup funding and company developments.")

# Task Configuration
st.header("Task Configuration")
task_name = st.text_input("Task Name", value="research_funded_startups")
task_description = st.text_area("Task Description", value="Investigate and compile information about biotech startups that have received significant funding in July 2024.")
task_expected_output = st.text_area("Expected Output", value="A detailed report on recently funded biotech startups, including company names, funding amounts, investors, date funding received, contacts from about us page, and the startups' focus areas within biotechnology.")

# Tool Selection
selected_tools = st.multiselect("Select Tools", ["InternetSearchTool"], default=["InternetSearchTool"])

if st.button("Generate Agent and Run"):
    if not openai_api_key:
        st.error("Please enter your OpenAI API Key")
    else:
        agent_yaml = f"""
        framework: "{framework}"
        topic: "{topic}"
        roles:
          {role_name}:
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
            with st.spinner("Running agent... This may take a few minutes."):
                praisonai = PraisonAI(agent_yaml=agent_yaml)
                result = praisonai.run()
            
            st.subheader("Agent Output")
            if result:
                st.markdown(result)
            else:
                st.warning("The agent did not produce any output. This might be due to an issue with the configuration or the API.")
            
            # Download buttons
            st.download_button(
                label="Download YAML Configuration",
                data=agent_yaml,
                file_name="agent_configuration.yaml",
                mime="application/x-yaml"
            )
            
            if result:
                st.download_button(
                    label="Download Agent Output",
                    data=result,
                    file_name="agent_output.md",
                    mime="text/markdown"
                )
        except Exception as e:
            st.error(f"An error occurred while running the agent: {str(e)}")
            st.error("If the error persists, please check your configuration and try again.")

# Display logs
if st.checkbox("Show logs"):
    st.text_area("Logs", value="INFO:__main__:Current SQLite version: 3.46.0\nINFO:__main__:Using SQLite version: 3.46.0", height=300)
