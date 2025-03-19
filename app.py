import streamlit as st
import pandas as pd
import os
import subprocess
from tempfile import NamedTemporaryFile

# Function to process the uploaded file using Ollama and Mistral
def process_invoice(file_path):
    # Read the file content
    with open(file_path, "r") as file:
        file_content = file.read()

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

    df = pd.DataFrame(data)
    return df

# Streamlit app
st.title("Invoice Extractor")
st.write("Upload an invoice to extract company, amount, and weight.")

# File upload
uploaded_file = st.file_uploader("Upload Invoice", type=["pdf", "txt", "docx"])

if uploaded_file is not None:
    # Save the uploaded file temporarily
    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    # Process the invoice
    st.write("Processing invoice...")
    df = process_invoice(tmp_file_path)

    # Display the extracted data
    st.write("Extracted Data:")
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

    # Clean up
    os.unlink(tmp_file_path)
