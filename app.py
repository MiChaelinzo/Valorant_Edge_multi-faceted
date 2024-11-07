import streamlit as st
import json
import pandas as pd
from PIL import Image, ImageOps, ImageDraw
import time
import requests

# Streamlit page configuration
st.set_page_config(
    page_title="VALORANT_EDGE: Your AI Esports Strategist",
    page_icon=":val:",
    layout="wide"
)

# Function to crop image into a circle
def crop_to_circle(image):
    mask = Image.new('L', image.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0) + image.size, fill=255)
    result = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
    result.putalpha(mask)
    return result

# Title
st.title("VALORANT_EDGE: Your AI Esports Strategist")

# Display a text box for input
prompt = st.text_input("Ask VALORANT_EDGE for advice or analysis:", max_chars=2000)
prompt = prompt.strip()

# Display a primary button for submission
submit_button = st.button("Submit", type="primary")

# Sidebar for user input
st.sidebar.title("Agent Insights")

# Session State Management
if 'history' not in st.session_state:
    st.session_state['history'] = []

# Mock API Endpoint (Replace with your actual API)
VALORANT_EDGE_API_ENDPOINT = "/api/valorant-edge" 

# Function to make API call to VALORANT Edge (using requests)
def get_valorant_edge_response(prompt):
    try:
        response = requests.post(VALORANT_EDGE_API_ENDPOINT, json={"question": prompt}) 

        if response.status_code == 200:
            data = response.json()
            return data.get("response", "No response from VALORANT_EDGE.") 
        else:
            return f"Error: {response.status_code} - Unable to connect to VALORANT_EDGE."
    except requests.exceptions.RequestException as e:
        return f"Error: An error occurred: {e}"


# Handling user input and responses
if submit_button and prompt:
    st.session_state['history'].append({"question": prompt, "answer": "..."}) 

    response = get_valorant_edge_response(prompt)

    # Update the answer in the history
    st.session_state['history'][-1]["answer"] = response

    # Rerun Streamlit to update the UI with the answer
    st.rerun()  # Use st.rerun() instead of st.experimental_rerun()

st.write("## Conversation History")

# Load images outside the loop
human_image = Image.open('val.png')
robot_image = Image.open('val1.jpg')
circular_human_image = crop_to_circle(human_image)
circular_robot_image = crop_to_circle(robot_image)

for index, chat in enumerate(reversed(st.session_state['history'])):
    col1_q, col2_q = st.columns([1, 11])
    with col1_q:
        st.image(circular_human_image, width=50)
    with col2_q:
        st.text_area("You:", value=chat["question"], height=50, key=f"question_{index}", disabled=True)

    col1_a, col2_a = st.columns([1, 11])
    with col1_a:
        st.image(circular_robot_image, width=50)
    with col2_a:
        st.text_area("VALORANT_EDGE:", value=chat["answer"], height=100, key=f"answer_{index}", disabled=True)

# Example Prompts Section
st.write("## Example Prompts")

example_prompts = [
    "I'm having trouble winning pistol rounds on Bind.",
    "What's the best agent composition for attacking Haven?",
    "How can I improve my aim with the Vandal?", 
    "What are some good strategies for playing as Cypher on Split?"
]

st.markdown(
    """
    Here are some examples to get you started:
    * **Match Analysis:** "Analyze my last match. I played Reyna on Ascent." (Provide match ID if possible)
    * **Agent Tips:** "Give me tips for playing as Killjoy on defense."
    * **Strategy:**  "What's a good strategy for retaking A Site on Icebox?" 
    * **Meta:** "What are the best Controllers in the current meta?" 
    """
)

for prompt in example_prompts:
    st.write(f"* {prompt}") 
