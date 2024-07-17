import streamlit as st
from openai import OpenAI
import re

# Set Streamlit page configuration
st.set_page_config(page_title="Chatbot with Image Generation")

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

def chat_with(prompt):
    messages = [
        {"role": "system", "content": "You are a helpful assistant. When explaining processes or giving instructions, please limit your response to 6-7 clear, concise steps."},
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

# Chat input
if prompt := st.chat_input("You:"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = chat_with(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    with st.chat_message("assistant"):
        st.markdown(response)
        
        response = re.sub(r'^\d+\.\s*', '', response, flags=re.MULTILINE)
        sentences = re.split(r'(?<=\.)\s+', response.strip())
        sentences = [sentence if sentence.endswith('.') else sentence + '.' for sentence in sentences]

        for c, sentence in enumerate(sentences, 1):
            image_url = generate_image(sentence)
            st.image(image_url, caption=f"Step {c}")

# Quit button
if st.button("Quit Chat"):
    st.session_state.messages = []
    st.experimental_rerun()
             
