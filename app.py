import streamlit as st
import pandas as pd
import ollama
import fitz  # PyMuPDF for PDF parsing
import io

# Function to extract invoice details based on the prompt
def extract_invoice_details(prompt, text):
    model = ollama.Model('mistral')
    response = model.prompt({
        'prompt': prompt,
        'context': text
    })
    return response.get('text', '')

# Function to handle file upload and extract text
def process_invoice(uploaded_file, prompt):
    try:
        # Read the uploaded file as a binary stream
        file_bytes = uploaded_file.read()

        # Check file type and read accordingly
        if uploaded_file.type == "text/plain":
            # Read as plain text
            invoice_text = file_bytes.decode('utf-8')
        elif uploaded_file.type == "application/pdf":
            # Use PyMuPDF to extract text from PDF
            pdf_file = io.BytesIO(file_bytes)  # Convert bytes to a file-like object
            pdf = fitz.open(pdf_file)
            invoice_text = ""
            for page_num in range(pdf.page_count):
                page = pdf.load_page(page_num)
                invoice_text += page.get_text("text")  # Get text from each page

        else:
            return "Unsupported file type. Please upload a .txt or .pdf file."

        # Extract details based on the prompt
        extracted_details = extract_invoice_details(prompt, invoice_text)
        return extracted_details
    
    except Exception as e:
        return f"Error processing file: {e}"

# Streamlit app layout
st.title("Invoice Information Extractor")

# Upload invoice
uploaded_file = st.file_uploader("Upload your invoice", type=["txt", "pdf"])

if uploaded_file is not None:
    st.write("File uploaded successfully!")

    # Get a prompt from the user
    user_prompt = st.text_input("Enter your prompt (e.g., 'Extract invoice number and amount')")

    if user_prompt:
        # Process the uploaded invoice
        extracted_data = process_invoice(uploaded_file, user_prompt)
        
        # Display the extracted information
        st.subheader("Extracted Information")
        st.write(extracted_data)

        # Option to download as Excel
        if st.button("Download as Excel"):
            df = pd.DataFrame([{'Extracted Data': extracted_data}])  # Create a DataFrame

            # Convert DataFrame to Excel
            excel_file = "extracted_invoice_data.xlsx"
            df.to_excel(excel_file, index=False)

            # Provide a download link
            st.download_button(
                label="Download Excel",
                data=open(excel_file, "rb"),
                file_name=excel_file
            )
