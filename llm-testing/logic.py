import json

import openai

client = openai.Client()

def addition(a : int, b : int) -> int:
    """Dummy logic function"""
    return a + b


def extract_profile_data(linkedin_text: str) -> dict:
    """
    Original version: Extract structured data from LinkedIn text with
    less strict constraints.
    """
    messages = [
        {"role": "system",
         "content": "You are an expert in extracting structured information "
                    "from text."},
        {"role": "user", "content": f"""
Extract the following structured information from the text below:
- Name
- Current Role
- Location
- Previous Roles
- Education

Text:
{linkedin_text}

Output the result as a JSON object.
"""}
    ]
    # LLM call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=messages
    )
    return json.loads(response.choices[0].message.content)


def extract_profile_data_strict(linkedin_text: str) -> dict:
    """
    New version: Extract structured data with stricter constraints
    (e.g., one role, specific formatting).
    """
    messages = [
        {"role": "system",
         "content": "You are an expert in extracting structured "
                    "information from text."},
        {"role": "user", "content": f"""
Extract the following structured information from the text below. Follow these guidelines:
- Name: Include only the person's full name.
- Current Role: Include only the most recent job title and company (one role and one company only).
- Location: Include only the city, state, and country.
- Previous Roles: List only the titles and companies (one entry per previous role, no additional details).
- Education: List only degree, field, and institution (one entry per degree).

Text:
{linkedin_text}

Output the result as a JSON object. Ensure the structure matches the requested format exactly.
"""}
    ]

    # LLM call with deterministic settings
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        #temperature=0,  # Ensures deterministic behavior
        response_format={"type": "json_object"},
        messages=messages
    )
    return json.loads(response.choices[0].message.content)