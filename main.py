import streamlit as st
from openai import OpenAI
import re

# Set Streamlit page configuration
st.set_page_config(page_title="Chatbot with Image Generation")

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Initialize chat history and active state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "active" not in st.session_state:
    st.session_state.active = True

def chat_with(prompt):
    messages = [
        {"role": "system", "content": "You are a helpful assistant. When explaining processes or giving instructions, please provide 6-7 clear, concise steps."},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message.content.strip()

def generate_image(prompt):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
        style="natural"
    )
    return response.data[0].url

# Streamlit app
st.title("Chatbot with Image Generation")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input and quit button
col1, col2 = st.columns([4, 1])
with col1:
    prompt = st.text_input("You:", disabled=not st.session_state.active)
with col2:
    quit_resume = st.button("Quit" if st.session_state.active else "Resume")

if quit_resume:
    st.session_state.active = not st.session_state.active
    st.experimental_rerun()

if prompt and st.session_state.active:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = chat_with(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    with st.chat_message("assistant"):
        response = re.sub(r'^\d+\.\s*', '', response, flags=re.MULTILINE)
        steps = re.split(r'(?<=\.)\s+', response.strip())
        steps = [step if step.endswith('.') else step + '.' for step in steps]

        for i, step in enumerate(steps, 1):
            st.markdown(f"Step {i}: {step}")
            image_url = generate_image(step)
            st.image(image_url, caption=f"Step {i}")

    st.experimental_rerun()
