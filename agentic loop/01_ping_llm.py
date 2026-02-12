"""Step 1: Ping an LLM - text in, text out."""

import os
import sys
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

query = sys.argv[1] if len(sys.argv) > 1 else "Who is Doug Turnbull? Reply in one sentence."

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=query
)

print(response.text)
