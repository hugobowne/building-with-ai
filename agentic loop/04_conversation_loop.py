"""
Step 4: Add a conversational loop - multi-turn interaction.

Key concepts:
- Outer loop: conversation turns (user inputs)
- Inner loop: agentic loop (tool calls until answer)
- Messages persist across turns, so follow-ups have context
- Note: context grows indefinitely - a real system would need to manage this
"""

import os
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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

# Messages persist across conversation turns - model remembers previous Q&A
messages = []

print("Research assistant ready. Type 'quit' to exit.\n")

# Outer loop: conversation turns
while True:
    user_input = input("You: ").strip()
    if user_input.lower() == "quit":
        break

    messages.append(types.Content(role="user", parts=[types.Part(text=user_input)]))

    # Inner loop: agentic loop (tool calls until model gives text answer)
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

            messages.append(types.Content(role="model", parts=[part]))
            messages.append(types.Content(role="user", parts=[types.Part(text=f"Search results:\n{results_text}")]))
        else:
            print(f"\nAssistant: {response.text}\n")
            # Save answer to messages so follow-up questions have context
            messages.append(types.Content(role="model", parts=[types.Part(text=response.text)]))
            break
