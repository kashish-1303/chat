import streamlit as st
from openai import OpenAI
import re
import traceback
import asyncio

# Set Streamlit page configuration
st.set_page_config(page_title="Chatbot with Image Generation")

# Logging function
def log(message):
    st.write(f"LOG: {message}")

try:
    log("App started")

    # Check for API key
    if "OPENAI_API_KEY" not in st.secrets:
        st.error("OPENAI_API_KEY is not set in the secrets.")
        st.stop()

    log("API key found")

    # Initialize OpenAI client
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    log("OpenAI client initialized")

    async def chat_with_timeout(prompt, timeout=30):
        try:
            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                ),
                timeout=timeout
            )
            return response.choices[0].message.content.strip()
        except asyncio.TimeoutError:
            return "Request timed out"

    async def generate_image_timeout(prompt, timeout=60):
        try:
            response = await asyncio.wait_for(
                client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                    style="natural"
                ),
                timeout=timeout
            )
            return response.data[0].url
        except asyncio.TimeoutError:
            return "Image generation timed out"

    # Streamlit app
    st.title("Chatbot with Image Generation")

    user_input = st.text_input("You: ", "")

    if st.button("Send"):
        if user_input.lower() in ["quit", "exit", "bye"]:
            st.stop()

        log("Processing user input")

        response = asyncio.run(chat_with_timeout(user_input))
        log("Chat response received")

        response = re.sub(r'^\d+\.\s*', '', response, flags=re.MULTILINE)
        sentences = re.split(r'(?<=\.)\s+', response.strip())
        sentences = [sentence if sentence.endswith('.') else sentence + '.' for sentence in sentences]

        for c, sentence in enumerate(sentences, 1):
            st.write(f"Chatbot: Step {c} - {sentence}")
            
            log(f"Generating image for sentence {c}")
            image_url = asyncio.run(generate_image_timeout(sentence))
            
            if image_url == "Image generation timed out":
                st.write("Image generation timed out")
            else:
                st.image(image_url, caption=f"Generated Image for Step {c}")

        log("Processing complete")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.text(traceback.format_exc())

             
