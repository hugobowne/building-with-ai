import gradio as gr
from llama_index.core import VectorStoreIndex, Document
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import fitz  # PyMuPDF

# Function to extract text from the PDF
def extract_text_from_pdf(pdf_file):
    pdf_doc = fitz.open(stream=pdf_file, filetype="pdf")
    text = ""
    for page_num in range(pdf_doc.page_count):
        page = pdf_doc.load_page(page_num)
        text += page.get_text("text")
    return text

# Function to process the uploaded PDF and create an index
def process_pdf(pdf_file):
    extracted_text = extract_text_from_pdf(pdf_file)
    document = Document(text=extracted_text)

    # Specify a Hugging Face model for local embeddings
    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")


    index = VectorStoreIndex.from_documents([document], embed_model=embed_model)
    return index

# Function to query the PDF using Ollama API via LLAMAindex
def query_pdf(pdf, query):
    if pdf is None:
        return "Please upload a PDF."
    if not query.strip():
        return "Please enter a valid query."

    # Initialize the Ollama LLM with the desired model (e.g., LLaMA2)
    llm = Ollama(model="llama2", request_timeout=60.0)

    # Extract text from the PDF and index it
    index = process_pdf(pdf)

    # Set up the query engine with the Ollama LLM
    query_engine = index.as_query_engine(llm=llm)

    # Query the index using the user's question
    response = query_engine.query(query)

    return response.response

# Gradio interface setup
with gr.Blocks() as app:
    pdf_upload = gr.File(label="Upload PDF", type="binary")
    query_input = gr.Textbox(label="Ask a question about the PDF")
    output = gr.Textbox(label="Answer", interactive=False)

    query_button = gr.Button("Submit")
    
    query_button.click(fn=query_pdf, inputs=[pdf_upload, query_input], outputs=output)

app.launch()