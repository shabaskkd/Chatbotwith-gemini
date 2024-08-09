import os

import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai


# Load environment variables
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="Chat with Mediaone AI!",
    page_icon=":brain:",  # Favicon emoji
    layout="centered",  # Page layout option
)

# Display the logo at the top left corner
st.sidebar.image("images/M-ONE.png", use_column_width=True)

# Dropdown with AI logos (Disabled options included)
ai_options = {
    "Gemini": "images/Gemini-logo.png",
    "ChatGPT (not selectable)": "images/Chatgpt-logo.png",
    "Meta (not selectable)": "images/Meta_logo.png",
    "Copilot (not selectable)": "images/Copiolet-logo.png"
}

selected_ai = st.selectbox(
    "Choose an AI model",
    options=[key for key in ai_options.keys()],
    format_func=lambda x: f"{x} - {'(not selectable)' if 'not selectable' in x else ''}"
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Set up Google Gemini-Pro AI model
gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('gemini-pro')


# Function to translate roles between Gemini-Pro and Streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role


# Initialize chat session in Streamlit if not already present
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])


# Display the chatbot's title on the page
st.title(" MediaOne AI")
# Prevent selection of unselectable options
if "not selectable" in selected_ai:
    st.error("This option is not selectable. Please choose a different AI model.")
else:
# Display the chat history
for message in st.session_state.chat_session.history:
    with st.chat_message(translate_role_for_streamlit(message.role)):
        st.markdown(message.parts[0].text)

# Input field for user's message
user_prompt = st.chat_input(f"Ask M-One {selected_ai}...")
if user_prompt:
    # Add user's message to chat and display it
    st.chat_message("user").markdown(user_prompt)

    # Send user's message to Gemini-Pro and get the response
    gemini_response = st.session_state.chat_session.send_message(user_prompt)

    # Display Gemini-Pro's response
    with st.chat_message("assistant"):
        st.markdown(gemini_response.text)
