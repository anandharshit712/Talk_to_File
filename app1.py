import os
import streamlit as st
from langchain_community.llms import Ollama
import base64

# Initialize the local language model
ollama = Ollama(base_url="http://localhost:11434", model="gemma:7b")

# Directory to save uploaded files
UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_uploaded_file(uploaded_file):
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def read_file(file_path):
    # Function to read the content of the file
    with open(file_path, "r") as f:
        content = f.read()
    return content

# Initialize session state for prompts and responses
if "history" not in st.session_state:
    st.session_state.history = []
if "selected_file" not in st.session_state:
    st.session_state.selected_file = None

st.title("Multi-File Q&A with Local LLM")

# Sidebar for showing uploaded files
st.sidebar.title("Uploaded Files")

# Handle file uploads
uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True)

if uploaded_files:
    # Clear history when new files are uploaded
    st.session_state.history = []

    for uploaded_file in uploaded_files:
        file_path = save_uploaded_file(uploaded_file)
        st.write(f"Uploaded file: {uploaded_file.name}")

    # Reset selected file if needed
    st.session_state.selected_file = None

if os.path.exists(UPLOAD_DIR):
    uploaded_files_list = os.listdir(UPLOAD_DIR)
    if uploaded_files_list:
        for file_name in uploaded_files_list:
            st.sidebar.write(file_name)
    else:
        st.sidebar.write("No files uploaded yet.")
else:
    st.sidebar.write("No files uploaded yet.")

# Display previous prompts and responses
if st.session_state.history:
    for item in st.session_state.history:
        st.markdown(f"""
            <div style='display: flex; justify-content: space-between; margin-bottom: 10px;'>
                <div style='flex: 1; text-align: right;'><b>Q:</b> {item['question']}</div>
            </div>
            <div style='display: flex; justify-content: space-between; margin-bottom: 10px; margin-top: 10px;'>
                <div style='flex: 1; text-align: left;'><b>A:</b> {item['answer']}</div>
            </div>
            <hr>
        """, unsafe_allow_html=True)

# Creating the text input at the bottom of the page for the question input
input_placeholder = st.empty()
question = input_placeholder.text_input(label="Enter Prompt", label_visibility="hidden", placeholder="Ask a question about the uploaded files:", key="input")

# Handle question submission automatically
if question:
    all_answers = []
    for uploaded_file in uploaded_files:
        file_path = save_uploaded_file(uploaded_file)
        content = read_file(file_path)
        prompt = question + content
        answer = ollama(prompt)
        all_answers.append(f"Answer from {uploaded_file.name}: {answer}")

    # Store the question and all answers in session state
    st.session_state.history.append({"question": question, "answer": " ".join(all_answers)})

    # Clear the input box after submission
    input_placeholder.text_input("Ask a question about the uploaded files:")

    # Re-run the app to update the display
    st.rerun()

# CSS for positioning the input box at the bottom and styling
st.markdown("""
    <style>
        .stTextInput div {
            position: fixed;
            bottom: 20px;
            width: 42%;
            left: 38%;
            border-radius: 25px;
            border: none;
        }
        .stTextInput input {
            padding-left: 20px;
        }
    </style>
""", unsafe_allow_html=True)
