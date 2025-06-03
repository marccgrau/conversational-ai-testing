import base64
import os.path

import streamlit as st

base_path = (
    "./" if os.path.isfile("Simulator_Visualizer.py") else "./simulator/visualization/"
)
st.set_page_config(
    page_title="Simulator Visualizer",
    page_icon=base_path + "images/hsg-logo.png",
)


# Path to your image
image_path = base_path + "images/iwi-logo-rgb.png"

# Read and encode the image to base64
with open(image_path, "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode()

# Define the target URL
target_url = "https://iwi.unisg.ch/de/lehrstuehle/forschungsgruppe-prof-dr-ivo-blohm/"

# Create the HTML code for the clickable image
html_code = f'''
    <a href="{target_url}" target="_blank">
        <img src="data:image/png;base64,{encoded_image}" width="50%" style="display: block; margin-left: 0; margin-right: auto;" />
    </a>
    <div style="height: 20px;"></div>
'''

# Display the clickable image in Streamlit
st.markdown(html_code, unsafe_allow_html=True)

# st.image(base_path + 'images/plurai_logo.png', width=300)  # Added line to display the Plurai logo
st.write("### Welcome to IWI DialogDojo!")

st.markdown(
    """
   **DialogDojo** is a multi-agent framework designed to provide fine-grained diagnostics for Conversational AI systems.
    This demo allows you to explore the capabilities of DialogDojo's chat-agent simulator, which simulates thousands of edge-case scenarios to discover failure points, performance gaps, and inform optimization decisions for chat-agents.
"""
)
