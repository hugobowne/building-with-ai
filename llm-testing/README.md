# Mastering LLM Application Testing - Code Companion

This directory contains the companion code for the Lightning Lesson "Mastering LLM Application Testing".

It demonstrates how to use `pytest` and `pytest-harvest` to systematically test and evaluate the output of Large Language Models (LLMs), using LinkedIn profile data extraction as an example.

## Setup

1.  **Create a Virtual Environment:** It's recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows use `venv\Scripts\activate`
    ```

2.  **Install Dependencies:** Install the required Python packages.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set OpenAI API Key:** You need an OpenAI API key to run the code. Set it as an environment variable.
    ```bash
    export OPENAI_API_KEY='your-api-key-here'
    ```
    *(Replace `'your-api-key-here'` with your actual key)*

4.  **Data:** The code expects LinkedIn profile text files to be placed in a subdirectory named `data/`. Sample files (`*.txt`) should be put there.

## Usage

*   **Jupyter Notebook (`test.ipynb`):** This notebook provides a step-by-step walkthrough of the concepts, from basic LLM calls to validation and testing integration. Open and run the cells sequentially using Jupyter Lab or Jupyter Notebook.
*   **Pytest Tests (`test_logic.py`):** This file contains the automated tests for the extraction logic in `logic.py`. Run the tests from your terminal within the `llm-testing` directory:
    ```bash
    pytest -vv -rP test_logic.py
    ```
    This command runs the tests verbosely (`-vv`) and shows the output from the `test_print_results` function (`-rP`), which includes the accuracy breakdown. It will also generate a `logic_results_*.csv` file with detailed test outcomes.

## Watch the Lesson

For a full explanation of these concepts and the code, [watch the Lightning Lesson video here](https://maven.com/p/2fe5a8/mastering-llm-application-testing?utm_medium=ll_share_link&utm_source=instructor):

