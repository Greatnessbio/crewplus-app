import streamlit as st
import os
import yaml
from praisonai import PraisonAI
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_praisonai(agent_yaml):
    try:
        praisonai = PraisonAI(agent_yaml=agent_yaml)
        result = praisonai.run()
        return result
    except Exception as e:
        logger.error(f"Error running PraisonAI: {str(e)}")
        return None

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
        
        # Run PraisonAI
        with st.spinner("Running PraisonAI... This may take a few minutes."):
            result = run_praisonai(agent_yaml)
        
        # Display the result
        if result:
            st.subheader("PraisonAI Output")
            st.write(result)
        else:
            st.error("An error occurred while running PraisonAI. Please check the logs for more information.")

# Display PraisonAI version
import praisonai
st.sidebar.write(f"PraisonAI Version: {praisonai.__version__}")
