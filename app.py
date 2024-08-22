import os
import streamlit as st
from langchain_community.llms import Ollama
import csv
import PyPDF2
import json
import pandas as pd

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

def read_file_text(file_path):
    # Function to read the content of the file
    with open(file_path, "r") as f:
        content = f.read()
    return content

def read_csv(file_path):
    with open(file_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        data = '\n'.join(','.join(row) for row in csv_reader)
    return data

def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text = page.extract_text()
            return text

def read_excel(file_path):
    data = pd.read_excel(file_path)
    result = data.to_string()
    return result

def read(file_path):
    file_path = save_uploaded_file(uploaded_file)
    _, file_extension = os.path.splitext(file_path)
    if file_extension.lower() in ['.txt', '.c', '.cpp', '.sql', '.py']:
        return read_file_text(file_path)
    elif file_extension.lower() == '.csv':
        return read_csv(file_path)
    elif file_extension.lower() in ['.xls', '.xlsx']:
        return read_excel(file_path)
    elif file_extension.lower() == '.pdf':
        return read_pdf(file_path)
    else:
        raise ValueError("Unsupported file type {}".format(file_extension))

# Clear the session state at the start of the app
st.cache_data.clear()

# Initialize session state for prompts and responses
if "history" not in st.session_state:
    st.session_state.history = []

st.title("Multi-File Q&A with Local LLM")

uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_path = save_uploaded_file(uploaded_file)
        st.write(f"Uploaded file: {uploaded_file.name}")

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


# CSS for positioning the input box at the bottom and styling
st.markdown("""
    <style>
        .stTextInput div {
            position: fixed;
            bottom: 10px;
            width: 100%;
            max-width: 780px;
            left: 570px;
            height: 50px;
            border-radius: 50px;
            border: none;
        }
        .stTextInput input {
            padding-left: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Creating the text input at the bottom of the page for the question input
input_placeholder = st.empty()
with input_placeholder.container():
    st.write('<div class="input-container">', unsafe_allow_html=True)
    question = st.text_input(label="Enter Prompt", label_visibility="hidden", placeholder="Ask a question about the uploaded files:")
    st.write('</div>', unsafe_allow_html=True)

# Handle question submission automatically
if question:
    all_answers = []
    for uploaded_file in uploaded_files:
        content = read(file_path)
        prompt = question + content
        answer = ollama(prompt)
        all_answers.append(f"Answer from {uploaded_file.name}: {answer}")

    # Store the question and all answers in session state
    st.session_state.history.append({"question": question, "answer": " ".join(all_answers)})

    # Clear the input box after submission
    input_placeholder.text_input("Ask a question about the uploaded files:")

    # Re-run the app to update the display
    st.experimental_rerun()