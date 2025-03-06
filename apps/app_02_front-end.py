import gradio as gr
from llama_index.core import VectorStoreIndex, Document
import fitz  # PyMuPDF

# Function to extract text from the PDF
def extract_text_from_pdf(pdf_file):
    # `pdf_file` is already a bytes object, so we pass it directly to PyMuPDF
    pdf_doc = fitz.open(stream=pdf_file, filetype="pdf")  # Open the PDF from bytes
    text = ""
    
    # Extract text from each page
    for page_num in range(pdf_doc.page_count):
        page = pdf_doc.load_page(page_num)
        text += page.get_text("text")
    
    return text

# Function to process the uploaded PDF and create an index
def process_pdf(pdf_file):
    extracted_text = extract_text_from_pdf(pdf_file)  # Extract text from the uploaded PDF
    document = Document(text=extracted_text)  # Create a proper Document object
    index = VectorStoreIndex.from_documents([document])  # Create index from document
    return index

# Function to query the index
def query_pdf(pdf, query):
    index = process_pdf(pdf)  # Create an index from the uploaded PDF
    query_engine = index.as_query_engine()  # Create query engine
    response = query_engine.query(query)  # Query the index
    return response.response

# Gradio interface setup
with gr.Blocks() as app:
    pdf_upload = gr.File(label="Upload PDF", type="binary")  # Correct type set to "binary"
    query_input = gr.Textbox(label="Ask a question about the PDF")
    output = gr.Textbox(label="Answer")
    
    query_button = gr.Button("Submit")
    query_button.click(query_pdf, inputs=[pdf_upload, query_input], outputs=output)

app.launch()