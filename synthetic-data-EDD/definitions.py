import os
import json

# Hardcoded Definitions (Matching eval/data/*.json)
# This file defines the personas and scenarios used for synthetic data generation.
# It can also be run directly to save these definitions to JSON files.

personas_data = {
    "student": {
        "id": "student",
        "name": "Student",
        "description": "A student taking a course on LLM applications who is new to AI/ML and has basic programming knowledge but limited experience with LLMs and generative AI.",
        "goals": [
            "Understand fundamental concepts of LLM-powered applications",
            "Learn how to build simple apps with LLMs (RAG, agents, etc.)",
            "Complete course assignments and projects"
        ],
        "technical_level": "beginner"
    },
    "data_scientist": {
        "id": "data_scientist",
        "name": "Data Scientist",
        "description": "A data scientist with strong analytical skills and intermediate ML knowledge who wants to incorporate LLMs into their data analysis workflows and projects.",
        "goals": [
            "Implement LLM-powered solutions for data analysis",
            "Optimize prompting strategies and evaluation methods",
            "Combine traditional ML with generative AI approaches"
        ],
        "technical_level": "intermediate"
    },
    "ml_engineer": {
        "id": "ml_engineer",
        "name": "ML Engineer",
        "description": "An ML engineer with strong programming skills and production experience who is building LLM-based systems for deployment in real applications.",
        "goals": [
            "Build robust, production-ready LLM applications",
            "Optimize system performance, costs, and latency",
            "Implement monitoring, evaluation, and deployment pipelines"
        ],
        "technical_level": "advanced"
    }
}

# Scenarios data based on reading scenarios.json (simplified for prompt)
# The original scenarios.json has a root key "scenarios" containing a list
# We'll use a dictionary structure here for easier iteration
scenarios_data = {
    "cohort_student": {
        "description": "A student in the second cohort trying to evaluate their own implementations and understand what makes a good response.",
        "context": "Attended workshops on LLM apps, RAG, prompt engineering."
    },
    "general": {
        "description": "Questions about fundamental concepts, terminology, and principles of LLM-powered applications.",
        "context": "Seeking to understand core concepts from workshops."
    },
    "technical": {
        "description": "Technical questions about implementing specific components or techniques.",
        "context": "Working on building/improving a technical aspect."
    },
    "factual": {
        "description": "Factual questions about specific content presented in the workshops.",
        "context": "Trying to recall/clarify specific workshop info."
    }
}

# --- Main block to save definitions when script is run directly ---
if __name__ == "__main__":
    BASE_PATH = os.path.dirname(__file__) # Directory of this script (scratch)
    OUTPUT_DATA_PATH = os.path.join(BASE_PATH, 'data') # Subdirectory for output
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DATA_PATH, exist_ok=True)
    
    # Save Personas
    personas_output_path = os.path.join(OUTPUT_DATA_PATH, 'personas.json')
    print(f"Saving definitions to {personas_output_path}...")
    with open(personas_output_path, 'w') as f:
        json.dump(personas_data, f, indent=2)
    
    # Save Scenarios
    scenarios_output_path = os.path.join(OUTPUT_DATA_PATH, 'scenarios.json')
    print(f"Saving definitions to {scenarios_output_path}...")
    with open(scenarios_output_path, 'w') as f:
        json.dump(scenarios_data, f, indent=2)
        
    print("Definitions saved successfully.") 