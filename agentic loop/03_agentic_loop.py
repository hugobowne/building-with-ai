"""
Step 3: Build the agentic loop - model calls tools until satisfied.

Key concepts:
- Loop until model responds with text instead of a tool call
- Model decides when it has enough info (that's the "agentic" part)
- Messages accumulate: each search result stays in context for the next call
"""

import os
import sys
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

user_query = sys.argv[1] if len(sys.argv) > 1 else "Compare Doug Turnbull's work with John Berryman's contributions to search relevancy."

search_tool = types.Tool(function_declarations=[
    types.FunctionDeclaration(
        name="web_search",
        description="Search the web for current information about a topic",
        parameters={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
    )
])

config = types.GenerateContentConfig(
    tools=[search_tool],
    system_instruction="Always use the web_search tool to answer questions. Do not rely on your training data."
)

# Messages list grows with each tool call - this is the "memory" of the conversation
messages = [
    types.Content(role="user", parts=[types.Part(text=user_query)])
]

# Keep calling the model until it responds with text (not a tool call)
while True:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=messages,
        config=config
    )

    if not response.candidates or not response.candidates[0].content:
        print("Empty response, retrying...")
        continue

    part = response.candidates[0].content.parts[0]

    # If model wants to search, execute and continue loop
    if part.function_call:
        query = part.function_call.args["query"]
        print(f"Searching: {query}")

        results = requests.post(
            "https://api.exa.ai/search",
            headers={"x-api-key": os.getenv("EXA_API_KEY")},
            json={"query": query, "numResults": 3, "contents": {"text": True}}
        ).json()

        results_text = "\n\n".join(
            f"Title: {r['title']}\nURL: {r['url']}\nContent: {r.get('text', '')[:500]}"
            for r in results.get("results", [])
        )

        print(f"Results:\n{results_text}\n")

        # Add tool call and results to message history
        # Next iteration, model sees all previous searches and can decide if it needs more
        messages.append(types.Content(role="model", parts=[part]))
        messages.append(types.Content(role="user", parts=[types.Part(text=f"Search results:\n{results_text}")]))

    # If model responds with text, we're done
    else:
        print(f"\nAnswer:\n{response.text}")
        break
