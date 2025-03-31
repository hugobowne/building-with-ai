#!/usr/bin/env python3
"""
Minimal LLM-as-a-judge for RAG Evaluation

A simple script that uses GPT-4 to evaluate RAG responses using existing labeled data as examples.
"""

import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv
import argparse # Import argparse

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def evaluate_rag_response(question, new_response, good_examples, bad_examples):
    """Use GPT-4 to evaluate a RAG response with few-shot examples."""
    
    # Build the prompt with examples and the new response
    prompt = f"""You are evaluating the output of a RAG system for workshop transcripts. 

Question:
{question}

"""
    
    # Add good examples
    if good_examples:
        prompt += "### Good example(s):\n"
        for ex in good_examples:
            response_text = ex['response'][0] if isinstance(ex['response'], list) else str(ex['response'])
            prompt += f"{response_text}\n\n"
            prompt += f"Reason this was good: {ex.get('reason', 'No reason provided')}\n\n"
    
    # Add bad examples
    if bad_examples:
        prompt += "### Bad example(s):\n"
        for ex in bad_examples:
            response_text = ex['response'][0] if isinstance(ex['response'], list) else str(ex['response'])
            prompt += f"{response_text}\n\n"
            prompt += f"Reason this was bad: {ex.get('reason', 'No reason provided')}\n\n"
    
    # Add new response to evaluate
    prompt += f"""### New system response to evaluate:
{new_response}

### Evaluation criteria:
A response is acceptable (+1) if:
- It directly answers the question with specific details
- It is factually correct based on the workshop content
- It avoids hallucinations or made-up information

A response is unacceptable (-1) if:
- It's vague, generic, or off-topic
- It hallucinates or fabricates content
- It fails to address key parts of the question

### Format your reply like this:
Judgment: "+1" or "-1"
Reason: (brief explanation)
"""
    
    # Call GPT-4 to evaluate
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert evaluator for RAG systems."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )
    
    # Parse the result
    content = response.choices[0].message.content
    
    # Extract judgment
    if "Judgment: \"+1\"" in content or "Judgment: +1" in content:
        judgment = "pass"
    elif "Judgment: \"-1\"" in content or "Judgment: -1" in content:
        judgment = "fail"
    else:
        judgment = "unknown"
    
    # Extract reason
    reason_parts = content.split("Reason:", 1)
    reason = reason_parts[1].strip() if len(reason_parts) > 1 else "No reason provided"
    
    return judgment, reason

def main():
    """Run a simple test of the LLM judge."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Evaluate RAG responses using an LLM judge.")
    parser.add_argument("--input-file", required=True, help="Path to the JSON file containing responses to evaluate.")
    parser.add_argument("--examples-file", default="data/evaluated_responses_20250328_190348.json",
                        help="Path to the JSON file containing labeled examples for few-shot learning.")
    parser.add_argument("--limit", type=int, help="Limit evaluation to the first N responses.")
    parser.add_argument("--output-prefix", default="llm_evaluated",
                        help="Prefix for the timestamped output file and the _all.json file.")
    args = parser.parse_args()

    print("Loading data...")
    
    # Path to data directory (relative to this script)
    # data_dir = "data" # No longer needed if full paths are used in args
    
    # Load examples (for few-shot learning)
    try:
        with open(args.examples_file, 'r') as f:
            examples = json.load(f)
        print(f"Loaded {len(examples)} examples from {args.examples_file}")
    except Exception as e:
        print(f"Error loading examples file {args.examples_file}: {e}")
        print("Proceeding without few-shot examples.")
        examples = [] # Ensure examples is defined

    # Load responses to evaluate
    try:
        with open(args.input_file, 'r') as f:
            to_evaluate = json.load(f)
        print(f"Loaded {len(to_evaluate)} responses from {args.input_file}")
    except Exception as e:
        print(f"Error loading input file {args.input_file}: {e}")
        return # Exit if we can't load responses

    # Apply limit if provided
    if args.limit and args.limit > 0 and args.limit < len(to_evaluate):
        to_evaluate = to_evaluate[:args.limit]
        print(f"LIMIT MODE: Evaluating only the first {len(to_evaluate)} responses.")
    
    # Select a few examples (if loaded)
    good_examples = []
    bad_examples = []
    if examples:
        good_examples = [ex for ex in examples if ex.get('judgment') == 'pass'][:1]
        bad_examples = [ex for ex in examples if ex.get('judgment') == 'fail'][:1]
        print(f"Using {len(good_examples)} good and {len(bad_examples)} bad examples for few-shot.")

    # Evaluate responses
    results = []
    total_responses_to_process = len(to_evaluate)
    print(f"Starting evaluation of {total_responses_to_process} responses...")
    
    for i, item in enumerate(to_evaluate):
        print(f"\nEvaluating response {i+1}/{total_responses_to_process}...")
        
        question = item['question']
        if isinstance(item['response'], list):
            response_text = item['response'][0]
        else:
            response_text = str(item['response'])
        
        print(f"Question: {question[:50]}...")
        
        # Evaluate with GPT-4
        judgment, reason = evaluate_rag_response(
            question, 
            response_text, 
            good_examples, 
            bad_examples
        )
        
        print(f"Judgment: {judgment}")
        print(f"Reason: {reason[:100]}...")
        
        # Save result
        item['judgment'] = judgment
        item['reason'] = reason
        item['evaluation_type'] = 'llm'
        results.append(item)

        # TEMPORARY: Limit to 2 evaluations for testing # <<< REMOVED THIS BLOCK
        # if i >= 1: # i is zero-indexed, so 0 and 1 make 2 iterations
        #     print("\\nLIMIT REACHED: Stopping after 2 evaluations for testing.")
        #     break
        
        # Wait a bit between calls
        time.sleep(1)
    
    # Save results to a new file with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Use the prefix from args for output files
    output_dir = os.path.dirname(args.input_file) # Save output in the same dir as input by default
    # --- Make prefix robust: strip potential directory path --- 
    base_prefix = os.path.basename(args.output_prefix)
    # --- Use base_prefix for filenames --- 
    timestamped_filename = f"{base_prefix}_{timestamp}.json"
    output_filename = os.path.join(output_dir, timestamped_filename)
    
    with open(output_filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nEvaluation complete! Results saved to {output_filename}")
    
    # Also save to the _all file expected by the viewer
    # --- Use base_prefix here too --- 
    all_output_filename = os.path.join(output_dir, f"{base_prefix}_all.json")
    with open(all_output_filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Also saved results to {all_output_filename}")
    print("You can view them with the JSON viewer.")

if __name__ == "__main__":
    main() 