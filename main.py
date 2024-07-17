import streamlit as st
from openai import OpenAI
import re

# Set Streamlit page configuration
st.set_page_config(page_title="Chatbot with Image Generation")

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Initialize chat history, step counter, and active state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_step" not in st.session_state:
    st.session_state.current_step = 0
if "steps" not in st.session_state:
    st.session_state.steps = []
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

# Quit button
if st.button("Quit" if st.session_state.active else "Resume"):
    st.session_state.active = not st.session_state.active

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("You:", disabled=not st.session_state.active):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if st.session_state.active:
        response = chat_with(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        with st.chat_message("assistant"):
            st.markdown("I've prepared the steps for you. Click 'Next Step' to see each step with its corresponding image.")
            
            response = re.sub(r'^\d+\.\s*', '', response, flags=re.MULTILINE)
            st.session_state.steps = re.split(r'(?<=\.)\s+', response.strip())
            st.session_state.steps = [step if step.endswith('.') else step + '.' for step in st.session_state.steps]
            st.session_state.current_step = 0

# Next step button
if st.button("Next Step", disabled=not st.session_state.active) and st.session_state.steps:
    if st.session_state.current_step < len(st.session_state.steps):
        step = st.session_state.steps[st.session_state.current_step]
        with st.chat_message("assistant"):
            st.markdown(f"Step {st.session_state.current_step + 1}: {step}")
            image_url = generate_image(step)
            st.image(image_url, caption=f"Step {st.session_state.current_step + 1}")
        st.session_state.current_step += 1
    else:
        st.write("All steps completed.")

# Reset button
if st.button("Reset Steps", disabled=not st.session_state.active):
    st.session_state.current_step = 0
    st.experimental_rerun()
