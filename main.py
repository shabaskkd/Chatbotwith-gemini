import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
import openai
import time
from groq import Groq  # Import Groq for Meta AI

# Load environment variables
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="Chat with MediaOne AI!",
    page_icon=":brain:",  # Favicon emoji
    layout="centered",  # Page layout option
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Set up Google Gemini-Pro AI model
gen_ai.configure(api_key=GOOGLE_API_KEY)
gemini_model = gen_ai.GenerativeModel('gemini-pro')

# Set your OpenAI API key
openai.api_key = OPENAI_API_KEY

# Initialize the Groq client for Meta AI
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    groq_client = None  # Handle missing API key for Groq/Meta AI

conversation = []  # Conversation history for ChatGPT

def get_gpt_response(user_input):
    message = {
        "role": "user",
        "content": user_input
    }
    conversation.append(message)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation
        )

        response_message = response['choices'][0]['message']
        conversation.append(response_message)
        return response_message['content']

    except openai.error.RateLimitError:
        st.error("Rate limit exceeded. Waiting before retrying...")
        time.sleep(60)  # Wait for 60 seconds before retrying
        return "I'm sorry, I'm currently experiencing high demand. Please try again in a moment."

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return "An error occurred while processing your request. Please try again later."

def get_meta_ai_response(user_input):
    if groq_client is None:
        return "Meta AI is not configured."

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_input,
                }
            ],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content

    except Exception as e:
        st.error(f"An error occurred with Meta AI: {e}")
        return "An error occurred while processing your request with Meta AI. Please try again later."

# Function to translate roles between Gemini-Pro and Streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role

# Initialize chat session in Streamlit if not already present
if "chat_session" not in st.session_state:
    st.session_state.chat_session = gemini_model.start_chat(history=[])

# Display the logo at the top left corner
st.sidebar.image("/root/Chatbotwith-gemini/images/M-ONE.png", use_column_width=True)

# Display the chatbot's title on the page
st.title("MediaOne AI")

# Dropdown to select AI provider
ai_provider = st.selectbox("Choose AI Provider", ["MOne_AI", "Third_Party AI"])

if ai_provider == "MOne_AI":
    st.info("MOne_AI is currently not configured.")
else:
    # Create columns for checkboxes and logos in a single line
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        selected_gemini = st.checkbox("Gemini", value=True)
        st.image("images/Gemini-logo.png", width=50)

    with col2:
        selected_chatgpt = st.checkbox("ChatGPT", value=False)
        st.image("images/Chatgpt-logo.png", width=50)

    with col3:
        selected_meta_ai = st.checkbox("Meta AI", value=False)
        st.image("images/Meta-logo.png", width=50)

    with col4:
        st.checkbox("Copilot", value=False, disabled=True)
        st.image("images/Copiolet-logo.png", width=50)

    # Input field for user's message
    user_prompt = st.chat_input(f"Ask the AI...")

    # Display the chat history and input based on the selected AI
    if user_prompt:
        st.chat_message("user").markdown(user_prompt)

        if selected_gemini:
            gemini_response = st.session_state.chat_session.send_message(user_prompt)
            with st.chat_message("assistant"):
                st.markdown("**Gemini Response:**")
                st.markdown(gemini_response.text)

        if selected_chatgpt:
            gpt_response = get_gpt_response(user_prompt)
            with st.chat_message("assistant"):
                st.markdown("**ChatGPT Response:**")
                st.markdown(gpt_response)

        if selected_meta_ai:
            meta_ai_response = get_meta_ai_response(user_prompt)
            with st.chat_message("assistant"):
                st.markdown("**Meta AI Response:**")
                st.markdown(meta_ai_response)
