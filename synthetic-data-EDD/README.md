# Synthetic Data Generation & Evaluation for LLM Apps

This directory contains scripts and data for experimenting with synthetic data generation and evaluation-driven development (EDD) for Large Language Model (LLM) applications. It mirrors parts of the main `eval` directory but is focused on demonstrating a specific workflow.

## The Evaluation-Driven Development (EDD) Flywheel

This setup demonstrates a practical EDD workflow, creating a continuous improvement cycle for LLM applications:

1.  **Define Test Cases:** Start by defining representative user personas and scenarios (`definitions.py`) that capture expected usage patterns.
2.  **Generate Synthetic Data:** Automatically create relevant test questions based on these definitions (`synthetic_data_generator.py`). This enables testing even without real user data.
3.  **Generate Responses:** Run the synthetic questions through your LLM system (e.g., an initial RAG setup) to get baseline responses.
4.  **Manual Labeling (Ground Truth):** Manually label a subset of responses (e.g., 20-100 examples) as "pass" or "fail" with reasons, using tools like `manual_evaluator.html`. This builds the ground truth needed for reliable evaluation.
5.  **Iterate & Compare:** Improve your system (e.g., try new models like Gemini, refine prompts, enhance retrieval). Generate responses from the updated system using the same questions. Use viewers like `compare_viewer.html` to see side-by-side differences.
6.  **Automated Evaluation (LLM-as-Judge):** Leverage the manually labeled data to configure an LLM to act as an automated judge (`simple_llm_judge.py`). This allows for consistent evaluation of large response sets.
7.  **Analyze & Improve:** Use viewers like `evaluation_comparison.html` to analyze the automated evaluation results. Identify patterns (e.g., specific scenarios where one model fails) and use these insights to guide the next round of system improvements.

This cycle (**Define -> Generate Data -> Generate Responses -> Label -> Evaluate -> Analyze -> Improve**) forms an EDD flywheel, driving continuous enhancement of your LLM application based on measurable quality signals.

## Prerequisites & Setup

Before running the lesson steps, ensure you have:

*   Python 3.x installed.
*   Access to an OpenAI API key.
*   (Optional) Access to a Gemini API key if you plan to use `simple_llm_judge.py` with Gemini or adapt scripts for it.

**Setup Steps:**

1.  **Install Dependencies:** Open your terminal in the **project root directory** (the parent of `synthetic-data-EDD/`) and run:
    ```bash
    pip install -r synthetic-data-EDD/requirements.txt
    ```
2.  **Configure API Keys:**
    *   In the **project root directory** (one level above this `synthetic-data-EDD/` directory), create a file named `.env`.
    *   Add your OpenAI API key to the `.env` file:
        ```
        OPENAI_API_KEY='your_api_key_here'
        ```
    *   *(Optional)* If needed, add your Gemini API key:
        ```
        GEMINI_API_KEY='your_gemini_key_here'
        ```
3.  **(For Viewers) Start a Simple HTTP Server:** The HTML viewers need to be served. Open a terminal **inside the `synthetic-data-EDD/` directory** and run:
    ```bash
    python -m http.server
    ```
    Keep this server running in the background. You can then access viewers at `http://localhost:8000/viewers/viewer_name.html`.

## Lightning Lesson Steps

Follow these steps to walk through the synthetic data generation and evaluation process:

1.  **Generate Personas & Scenarios:**
    *   The `definitions.py` script contains hardcoded Python dictionaries defining relevant user personas and scenarios. Running it saves them to JSON.
    *   **Command (run from project root):**
        ```bash
        python synthetic-data-EDD/definitions.py
        ```
    *   **Output:** Creates `synthetic-data-EDD/data/personas.json` and `synthetic-data-EDD/data/scenarios.json`.

2.  **Generate Synthetic Questions:**
    *   The `synthetic_data_generator.py` script uses the generated JSON definitions and the OpenAI API (requires `OPENAI_API_KEY` in the root `.env`) to create test questions.
    *   **Command (run from project root):**
        ```bash
        python synthetic-data-EDD/synthetic_data_generator.py
        ```
    *   **Output:** Creates `synthetic-data-EDD/data/questions.json`.

3.  **Manual Labeling (Simulated):**
    *   **Concept:** In a real workflow, you'd run the generated `questions.json` through your model to get responses (example files like `data/responses_*.json` might already exist here for demo purposes). You would then manually label a subset (e.g., 20-50) as "pass" or "fail" with reasons to create ground truth.
    *   **Tool:** The `manual_evaluator.html` viewer helps with this labeling. It loads a response file and saves your judgments.
    *   **Action (Demo):** Open the viewer in your browser (requires the HTTP server from Setup Step 3 to be running):
        ```bash
        # In browser: http://localhost:8000/viewers/manual_evaluator.html
        # Or via command line (macOS):
        open http://localhost:8000/viewers/manual_evaluator.html
        ```
    *   *(In a real scenario, you would use this viewer to label your actual model outputs).*

4.  **Side-by-Side Comparison (Simulated):**
    *   **Concept:** When comparing different models or system versions, you need to see their responses side-by-side for the same questions.
    *   **Tool:** The `compare_viewer.html` loads a combined file (e.g., `data/model_comparison_*.json`) showing responses from multiple sources.
    *   **Action (Demo):** Open the viewer (requires HTTP server):
        ```bash
        # In browser: http://localhost:8000/viewers/compare_viewer.html
        # Or via command line (macOS):
        open http://localhost:8000/viewers/compare_viewer.html
        ```
    *   *(In a real scenario, you would examine the qualitative differences displayed here).*

5.  **Automated Evaluation (LLM-as-Judge):**
    *   **Concept:** Use the manually labeled examples (`--examples-file`) as few-shot prompts to guide a powerful LLM (like GPT-4o) in evaluating a larger set of responses (`--input-file`) automatically via `simple_llm_judge.py`.
    *   **Command (Example - run from project root):**
        ```bash
        # Ensure file paths exist or use your actual file names
        # Add --limit 2 for a quick test during the lesson:
        python synthetic-data-EDD/simple_llm_judge.py \
            --input-file synthetic-data-EDD/data/responses_gemini_20250328_224605.json \
            --examples-file synthetic-data-EDD/data/evaluated_responses_20250328_190348.json \
            --output-prefix synthetic-data-EDD/data/gemini_llm_evaluated \
            --limit 2
        ```
    *   **Output:** The script saves evaluated results (including pass/fail judgment and reason from the LLM judge) to timestamped and `_all.json` files (e.g., `gemini_llm_evaluated_*.json`) in the data directory. If using `--limit`, fewer results will be generated.

6.  **Analyze Automated Evaluations:**
    *   **Concept:** Compare the automated evaluation results across different models or versions.
    *   **Tool:** The `evaluation_comparison.html` viewer loads evaluation files and compares the judgments and reasons side-by-side.
    *   **Action (Demo):** Open the viewer (requires HTTP server). **Note:** This viewer currently loads two specific, hardcoded evaluation files by default (see comments in the HTML source). You may need to modify the HTML to view different files.
        ```bash
        # In browser: http://localhost:8000/viewers/evaluation_comparison.html
        # Or via command line (macOS):
        open http://localhost:8000/viewers/evaluation_comparison.html
        ```
    *   *(This completes the demo loop, showing how to quantitatively assess performance differences).*

## Reference: Directory Contents

*   **Scripts (`.py`):**
    *   `definitions.py`: Defines hardcoded user personas & scenarios; run to generate JSON.
    *   `synthetic_data_generator.py`: Generates synthetic questions using OpenAI API based on definitions.
    *   `simple_llm_judge.py`: Evaluates model responses using an LLM judge and labeled examples.
    *   `requirements.txt`: Python package dependencies.
*   **Data (`data/`):**
    *   `personas.json` / `scenarios.json`: Definitions saved by `definitions.py`.
    *   `questions.json`: Synthetic questions generated by `synthetic_data_generator.py`.
    *   `responses_*.json` / `model_comparison_*.json`: Example model responses (often manually added/copied for demo).
    *   `evaluated_*.json` / `llm_evaluated_*.json`: Example evaluation results (often manually added/copied for demo or generated by `simple_llm_judge.py`).
*   **Viewers (`viewers/`):**
    *   HTML files (`manual_evaluator.html`, `compare_viewer.html`, `evaluation_comparison.html`) for visualizing data and facilitating the workflow steps. Require an HTTP server to run.

*(More context or next steps can be added here later.)* 