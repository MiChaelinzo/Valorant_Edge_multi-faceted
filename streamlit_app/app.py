import invoke_agent as agenthelper
import streamlit as st
import json
import pandas as pd
from PIL import Image, ImageOps, ImageDraw
import boto3
import os

os.environ["AWS_ACCESS_KEY_ID"] = aws_access_key_id
os.environ["AWS_SECRET_ACCESS_KEY"] = aws_secret_access_key

# Access AWS credentials from Streamlit secrets
aws_access_key_id = st.secrets["aws"]["access_key_id"]
aws_secret_access_key = st.secrets["aws"]["secret_access_key"]

# Initialize a boto3 session
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# Retrieve credentials
credentials = session.get_credentials().get_frozen_credentials()

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

# Function to parse and format response
def format_response(response_body):
    try:
        data = json.loads(response_body)
        if isinstance(data, list):
            return pd.DataFrame(data)
        else:
            return response_body
    except json.JSONDecodeError:
        return response_body

# Orchestration
def main():
    st.title("VALORANT_EDGE: Your AI Esports Strategist")

    prompt = st.text_input("Ask VALORANT_EDGE for advice or analysis:", max_chars=2000)
    prompt = prompt.strip()

    submit_button = st.button("Submit", type="primary")
    end_session_button = st.button("End Session")

    if 'history' not in st.session_state:
        st.session_state['history'] = []
    if 'trace_data' not in st.session_state:
        st.session_state['trace_data'] = ""

    if submit_button and prompt:
        event = {
            "sessionId": "VALORANT_SESSION",
            "question": prompt
        }
        response = agenthelper.lambda_handler(event, None)
        
        try:
            if response and 'body' in response and response['body']:
                response_data = json.loads(response['body'])
                print("TRACE & RESPONSE DATA ->  ", response_data)
            else:
                print("Invalid or empty response received")
        except json.JSONDecodeError as e:
            print("JSON decoding error:", e)
            response_data = None 
        
        try:
            all_data = format_response(response_data['response'])
            the_response = response_data['trace_data']
        except:
            all_data = "..." 
            the_response = "Apologies, but an error occurred. Please rerun the application" 

        st.sidebar.text_area("Trace Data:", value=all_data, height=700)
        st.session_state['history'].append({"question": prompt, "answer": the_response})
        st.session_state['trace_data'] = the_response

    if end_session_button:
        st.session_state['history'].append({"question": "Session Ended", "answer": "Thank you for using VALORANT_EDGE!"})
        event = {
            "sessionId": "VALORANT_SESSION",
            "question": "placeholder to end session",
            "endSession": True
        }
        agenthelper.lambda_handler(event, None)
        st.session_state['history'].clear()

    display_conversation_history()
    display_example_prompts()

def display_conversation_history():
    st.write("## Conversation History")

    human_image = Image.open('val.png')
    robot_image = Image.open('val1.jpg')
    circular_human_image = crop_to_circle(human_image)
    circular_robot_image = crop_to_circle(robot_image)

    for index, chat in enumerate(reversed(st.session_state['history'])):
        col1_q, col2_q = st.columns([1, 11])
        with col1_q:
            st.image(circular_human_image, width=50)
        with col2_q:
            st.text_area("You:", value=chat["question"], height=150, key=f"question_{index}", disabled=True)

        col1_a, col2_a = st.columns([1, 11])
        with col1_a:
            st.image(circular_robot_image, width=100)
        with col2_a:
            if isinstance(chat["answer"], pd.DataFrame):
                st.dataframe(chat["answer"], key=f"answer_df_{index}")
            else:
                st.text_area("VALORANT_EDGE:", value=chat["answer"], height=250, key=f"answer_{index}", disabled=True)

def display_example_prompts():
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

if __name__ == "__main__":
    main()
