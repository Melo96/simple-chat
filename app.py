import io
import base64
import fitz
import streamlit as st
from openai import OpenAI
from PIL import Image

# Set OpenAI API key from Streamlit secrets
client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

def img_clicked():
    st.session_state.img_clicked = True

def pdf_clicked():
    st.session_state.pdf_clicked = True

def load_img(img_file_buffer):
    image = Image.open(img_file_buffer)
    # Convert to bytes
    with io.BytesIO() as output:
        image.save(output, format="JPEG")
        image_bytes = output.getvalue()

    st.session_state.encoded_imgs.append(base64.b64encode(image_bytes).decode('utf-8'))

def load_pdf(pdf_file_buffer):
    doc = fitz.open("pdf", pdf_file_buffer.read())

    # 遍历每一页
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # 加载页面
        pix = page.get_pixmap()  # 获取页面的像素图

        # 将像素图转换为 PIL 图像
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # 将像素图保存为 JPEG 格式的字节流
        with io.BytesIO() as output:
            img.save(output, format="JPEG")
            image_bytes = output.getvalue()
        st.session_state.encoded_imgs.append(base64.b64encode(image_bytes).decode('utf-8'))

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.encoded_imgs = []
    st.session_state.img_clicked = False
    st.session_state.pdf_clicked = False

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"]=='assistant':
            st.write(message["content"])
        elif message['role']=='user':
            for item in message["content"]:
                if item['type']=='text':
                    st.write(message['text'])

with st.sidebar:
    st.title("ChatGPT-like clone")
    col1, col2 = st.columns(2)
    with col1:
        st.button('Upload Image', on_click=img_clicked)
        if st.session_state.img_clicked:
            img_file_buffer = st.file_uploader('Upload an image', type=['png', 'jpg'])
            if img_file_buffer: load_img(img_file_buffer)
            
    with col2:
        st.button('Upload PDF', on_click=pdf_clicked)
        if st.session_state.pdf_clicked:
            pdf_file_buffer = st.file_uploader('Upload an image', type=['pdf'])
            if pdf_file_buffer: load_pdf(pdf_file_buffer)

# Accept user input
if text := st.chat_input("请在这里输入消息，点击Enter发送"):
    # Add user message to chat history
    message = {"role": "user", "content": [{"type": "text", "text": text}]}
    # Add uploaded image
    if st.session_state.encoded_imgs:
        for img in st.session_state.encoded_imgs:
            message['content'].append({"type": "image_url",
                                    "image_url": {
                                                        "url": f"data:image/jpeg;base64,{img}"
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
