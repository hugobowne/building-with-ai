from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from dotenv import load_dotenv
import os

load_dotenv()
print(f"API Key loaded: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")

documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("what is o1")
print(response)
