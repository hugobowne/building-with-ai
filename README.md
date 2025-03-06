# Building with AI: Practical LLM Workflows

This repository contains notebooks and code snippets for working with large language models (LLMs) in real-world applications. It will be updated with examples covering different workflows, integrations, and strategies for building LLM-powered applications.

## **Setting Up Your Python Environment**

We’ll be using **uv** to manage dependencies. This ensures a lightweight, reproducible Python environment.

#### **Install uv**
If you don’t have UV installed, first install it with:

```shell
pip install uv
```

#### **Create and activate your environment**

```shell
uv venv buildingai
```

Activate the environment:

- **On macOS/Linux:**  
  ```shell
  source buildingai/bin/activate
  ```
- **On Windows:**  
  ```shell
  buildingai\Scripts\activate
  ```

#### **Install dependencies**
Once the environment is active, install all required Python packages:

```shell
uv pip install -r requirements.txt
```

---

### **Running Jupyter Notebooks**

If you’re using Jupyter notebooks in this repository:
- **Select the correct Python interpreter** before running the notebook.
- Ensure that Jupyter is using the Python environment (`gemma-app`) you just created.
