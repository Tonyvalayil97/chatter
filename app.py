import streamlit as st
import os
from tempfile import NamedTemporaryFile
import PyPDF2  # For extracting text from PDFs
from sentence_transformers import SentenceTransformer  # For embeddings
from sklearn.metrics.pairwise import cosine_similarity  # For similarity search
import numpy as np

# Initialize the embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to extract text from a PDF file
def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

# Function to generate embeddings for text
def generate_embeddings(text):
    return embedding_model.encode(text)

# Function to perform similarity search
def retrieve_relevant_text(query_embedding, text_embeddings, texts, top_k=3):
    similarities = cosine_similarity([query_embedding], text_embeddings)[0]
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    return [texts[i] for i in top_indices]

# Function to interact with Ollama and Mistral
def ask_mistral(question, context):
    # Use Ollama to interact with Mistral
    command = f"ollama run mistral 'Answer this question based on the context: {question}. Context: {context}'"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

# Streamlit app
st.title("Invoice Query System")
st.write("Upload invoices and ask questions about them.")

# Allow multiple file uploads
uploaded_files = st.file_uploader("Upload Invoices", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    # Extract text from all uploaded files
    all_texts = []
    for uploaded_file in uploaded_files:
        with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        text = extract_text_from_pdf(tmp_file_path)
        all_texts.append(text)
        os.unlink(tmp_file_path)

    # Generate embeddings for all texts
    text_embeddings = [generate_embeddings(text) for text in all_texts]

    # Flatten texts and embeddings for retrieval
    all_texts_flat = [text for text in all_texts]
    text_embeddings_flat = np.array(text_embeddings)

    # User input for question
    question = st.text_input("Ask a question about the invoices:")

    if question:
        # Generate embedding for the question
        question_embedding = generate_embeddings(question)

        # Retrieve relevant text based on the question
        relevant_texts = retrieve_relevant_text(question_embedding, text_embeddings_flat, all_texts_flat)

        # Combine relevant texts into context
        context = " ".join(relevant_texts)

        # Ask Mistral the question
        answer = ask_mistral(question, context)
        st.write("Answer:")
        st.write(answer)
