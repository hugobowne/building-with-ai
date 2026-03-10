"""
Step 2: Add a tool - introduce the model to function calling.

Key concepts:
- Define a tool (web_search) that the model can choose to call
- System prompt forces grounding via search (reduces hallucination)
- After executing the tool, we send results back to the model for a final answer
- This is one-shot: one tool call, one answer. Step 3 adds looping.
"""

import os
import sys
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

user_query = sys.argv[1] if len(sys.argv) > 1 else "Who is Doug Turnbull? The search relevancy expert."

# Define a tool the model can call - Gemini uses this schema to know what's available
search_tool = types.Tool(function_declarations=[
    types.FunctionDeclaration(
        name="web_search",
        description="Search the web for current information about a topic",
        parameters={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
    )
])

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[
        types.Content(role="user", parts=[types.Part(text=user_query)])
    ],
    config=types.GenerateContentConfig(
        tools=[search_tool],
        system_instruction="Always use the web_search tool to answer questions. Do not rely on your training data."
    )
)

# Response contains either a function_call (model wants to use tool) or text (direct answer)
part = response.candidates[0].content.parts[0]
if part.function_call:
    search_query = part.function_call.args["query"]
    print(f"Model called web_search with: {search_query}\n")

    results = requests.post(
        "https://api.exa.ai/search",
        headers={"x-api-key": os.getenv("EXA_API_KEY")},
        json={"query": search_query, "numResults": 3, "contents": {"text": True}}
    ).json()

    # Debug: check if we got results
    print(f"Exa returned {len(results.get('results', []))} results\n")

    # Format results as text
    results_text = "\n\n".join(
        f"Title: {r['title']}\nURL: {r['url']}\nContent: {r.get('text', '')[:500]}"
        for r in results.get("results", [])
    )

    # Send results back to model for final answer
    # We reconstruct the conversation: user question -> model's tool call -> tool results
    final_response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            types.Content(role="user", parts=[types.Part(text=user_query)]),
            types.Content(role="model", parts=[part]),  # The tool call the model made
            types.Content(role="user", parts=[types.Part(text=f"Search results:\n{results_text}")])  # Tool output
        ],
        config=types.GenerateContentConfig(
            system_instruction="Answer based on the search results provided."
        )
    )
    if final_response.text:
        print(final_response.text)
    else:
        print(f"No text. Response: {final_response.candidates[0].content.parts[0]}")
