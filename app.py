import streamlit as st
import os
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *
from langchain_utils import invoke_chain

# Float feature initialization
float_init()

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hola! Como puedo ayudarte hoy?"}
        ]

initialize_session_state()

st.title("Chatbot 🤖, Asistente Virtual de Calidda")

# Create footer container for the microphone and text input
footer_container = st.container()
with footer_container:
    col1, col2 = st.columns([2, 1.5])  # Adjusted column proportions
    with col1:
        user_input = st.text_input("Escribe tu pregunta aquí:", "")
    with col2:
        audio_bytes = audio_recorder()

# Process text input
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

# Process audio input
if audio_bytes:
    with st.spinner("Transcribing..."):
        webm_file_path = "temp_audio.mp3"
        with open(webm_file_path, "wb") as f:
            f.write(audio_bytes)

        transcript = speech_to_text(webm_file_path)
        if transcript:
            st.session_state.messages.append({"role": "user", "content": transcript})
            with st.chat_message("user"):
                st.write(transcript)
            os.remove(webm_file_path)

# Generate assistant response if the last message is from the user
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking🤔..."):
            last_user_message = st.session_state.messages[-1]["content"]
            final_response = invoke_chain(last_user_message, st.session_state.messages)
        with st.spinner("Generating audio response..."):
            audio_file = text_to_speech(final_response)
            autoplay_audio(audio_file)
        st.markdown(final_response)
        st.session_state.messages.append({"role": "assistant", "content": final_response})
        os.remove(audio_file)

# Float the footer container and provide CSS to target it with
footer_container.float("bottom: 0rem;")