import os
import requests
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

search_tool = types.Tool(function_declarations=[
    types.FunctionDeclaration(
        name="web_search",
        description="Search the web for current information",
        parameters={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
    )
])

messages = []

while True:
    user_input = input("> ")
    if user_input.lower() == "quit":
        break

    messages.append(types.Content(role="user", parts=[types.Part(text=user_input)]))

    # Agentic loop
    while True:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[search_tool],
                system_instruction="Always use web_search to answer. Do not rely on training data."
            )
        )

        part = response.candidates[0].content.parts[0]

        if part.function_call:
            search_query = part.function_call.args["query"]
            print(f"Searching: {search_query}")

            results = requests.post(
                "https://api.exa.ai/search",
                headers={"x-api-key": os.getenv("EXA_API_KEY")},
                json={"query": search_query, "numResults": 3, "contents": {"text": True}}
            ).json()

            results_text = "\n\n".join(
                f"Title: {r['title']}\nURL: {r['url']}\nContent: {r.get('text', '')[:500]}"
                for r in results.get("results", [])
            )

            messages.append(types.Content(role="model", parts=[part]))
            messages.append(types.Content(role="user", parts=[types.Part(text=f"Search results:\n{results_text}")]))
        else:
            print(response.text)
            messages.append(types.Content(role="model", parts=[types.Part(text=response.text)]))
            break
