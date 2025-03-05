import os
import gradio as gr
from llama_index.core import VectorStoreIndex, Document
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import fitz  # PyMuPDF

# Function to extract text from the PDF
def extract_text_from_pdf(pdf_file_bytes):
    pdf_doc = fitz.open(stream=pdf_file_bytes, filetype="pdf")
    text = ""
    for page_num in range(pdf_doc.page_count):
        page = pdf_doc.load_page(page_num)
        text += page.get_text("text")
    return text

# Function to process the uploaded PDF and create an index
def process_pdf(pdf_file_bytes):
    extracted_text = extract_text_from_pdf(pdf_file_bytes)
    document = Document(text=extracted_text)

    # Specify a Hugging Face model for local embeddings
    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

    index = VectorStoreIndex.from_documents([document], embed_model=embed_model)
    return index

# Function to handle conversation, with option for model choice
def query_pdf(pdf, query, history, model_choice):
    if pdf is None:
        return [("Please upload a PDF.", "")], history
    if not query.strip():
        return [("Please enter a valid query.", "")], history

    try:
        # Choose between local (Ollama) or OpenAI model
        if model_choice == "Local (Ollama)":
            llm = Ollama(model="llama2", request_timeout=60.0)
        elif model_choice == "OpenAI":
            # Use OpenAI's model and access the API key from the environment variable
            openai_api_key = os.getenv("OPENAI_API_KEY")
            llm = OpenAI(api_key=openai_api_key, model="gpt-3.5-turbo")

        # Process the PDF and set up the query engine
        index = process_pdf(pdf)
        query_engine = index.as_query_engine(llm=llm)

        # Add previous conversation to the query for context
        conversation = "\n".join([f"User: {h[0]}\nAssistant: {h[1]}" for h in history])
        conversation += f"\nUser: {query}\n"

        # Query the index using the user's question with context
        response = query_engine.query(conversation)
        
    except Exception as e:
        return [("An error occurred", str(e))], history

    # Update conversation history
    history.append((query, response.response))
    return history, history

# Gradio interface setup
with gr.Blocks() as app:
    pdf_upload = gr.File(label="Upload PDF", type="binary")
    query_input = gr.Textbox(label="Ask a question about the PDF")
    model_choice = gr.Radio(label="Select Model", choices=["Local (Ollama)", "OpenAI"], value="Local (Ollama)")
    output = gr.Chatbot(label="Conversation")
    history_state = gr.State([])

    query_button = gr.Button("Submit")
    query_button.click(query_pdf, [pdf_upload, query_input, history_state, model_choice], [output, history_state])

app.launch()