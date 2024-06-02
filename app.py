import io
import base64
import streamlit as st
from openai import OpenAI
from PIL import Image

st.title("ChatGPT-like clone")

# Set OpenAI API key from Streamlit secrets
client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

with st.chat_message("assistant"):
    st.write('你怎么又来问问题啊')

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        for item in message["content"]:
            if item['type']=='text':
                st.write(message["content"])

with st.sidebar:
    st.container(height=500, border=False)
    img_file_buffer = st.file_uploader('Upload an image', type=['png', 'jpg'])
    encoded_img = None
    if img_file_buffer is not None:
        image = Image.open(img_file_buffer)
        # Convert to bytes
        with io.BytesIO() as output:
            image.save(output, format="JPEG")
            image_bytes = output.getvalue()

        encoded_img = base64.b64encode(image_bytes).decode('utf-8')

# Accept user input
if text := st.chat_input("请在这里输入消息，点击Enter发送"):
    # Add user message to chat history
    message = {"role": "user", "content": [{"type": "text", "text": text}]}
    # Add uploaded image
    if encoded_img:
        message['content'].append({"type": "image_url",
                                   "image_url": {
                                                    "url": f"data:image/jpeg;base64,{encoded_img}"
                                                }
                                })
    st.session_state.messages.append(message)
    # Display user message in chat message container
    with st.chat_message("user"):
        st.write(text)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model='gpt-4o',
            messages=st.session_state.messages,
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
