import os
import sys
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

query = sys.argv[1]

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=query
)

print(response.text)
