import streamlit as st
import pandas as pd
import os
import subprocess
from tempfile import NamedTemporaryFile
import PyPDF2  # For extracting text from PDFs

# Function to extract text from a PDF file
def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

# Function to process the uploaded file using Ollama and Mistral
def process_invoice(file_content):
    # Use Ollama to interact with Mistral
    # Replace this with your actual command to interact with Ollama and Mistral
    command = f"ollama run mistral 'Extract company, amount, and weight from this invoice: {file_content}'"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    # Parse the result (this is a placeholder, adjust based on your actual output)
    # Example output: "Company: Example Company, Amount: $1000, Weight: 50kg"
    output = result.stdout.strip()
    data = {"Company": [], "Amount": [], "Weight": []}

    # Extract data from the output (this is a simple example)
    if "Company:" in output:
        data["Company"].append(output.split("Company:")[1].split(",")[0].strip())
    if "Amount:" in output:
        data["Amount"].append(output.split("Amount:")[1].split(",")[0].strip())
    if "Weight:" in output:
        data["Weight"].append(output.split("Weight:")[1].strip())

    return data

# Streamlit app
st.title("Invoice Extractor")
st.write("Upload invoices to extract company, amount, and weight.")

# Allow multiple file uploads
uploaded_files = st.file_uploader("Upload Invoices", type=["pdf", "txt", "docx"], accept_multiple_files=True)

if uploaded_files:
    all_data = []  # To store extracted data from all files

    for uploaded_file in uploaded_files:
        # Save the uploaded file temporarily
        with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        # Extract text from the PDF
        file_content = extract_text_from_pdf(tmp_file_path)

        # Process the invoice
        st.write(f"Processing {uploaded_file.name}...")
        extracted_data = process_invoice(file_content)

        # Add file name to the extracted data
        extracted_data["File Name"] = uploaded_file.name
        all_data.append(extracted_data)

        # Clean up
        os.unlink(tmp_file_path)

    # Combine all extracted data into a single DataFrame
    if all_data:
        df = pd.DataFrame(all_data)
        st.write("Extracted Data from All Files:")
        st.dataframe(df)

        # Generate Excel file
        excel_file = "extracted_data.xlsx"
        df.to_excel(excel_file, index=False)
        st.download_button(
            label="Download Excel",
            data=open(excel_file, "rb").read(),
            file_name=excel_file,
            mime="application/vnd.ms-excel"
        )
