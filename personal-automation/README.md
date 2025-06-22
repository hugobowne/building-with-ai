# Personal Automation

This subdirectory contains code from the lightning talk [10x Your Productivity by Building Personal Agents with MCP](https://maven.com/p/05b8f8/10x-your-productivity-by-building-personal-agents-with-mcp).

## Quick Start

All the below comamnds assume you are running from the same directory this README is located in.
Explanations of several files can be found near the end of this README.

Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Sync environment:

```bash
uv sync
```

Run the sample MCP server:

```bash
uv run uvicorn minimal_fastmcp:sse_app --port 8082
```

List available tools on the MCP server:

```bash
uv run minimal_fastmcp.py
```

Call a tool on the MCP server:

```bash
uv run minimal_fastmcp.py add '{"a": 1, "b": 2}'
```

Run a simple agent:

```bash
uv run simple_mirascope_agent.py 'what is 1 + 1?'
```

Great! You have the basic examples working. Follow the pre-requisite setup steps below to run the more feature-complete examples!

## Setup

Below are some setup steps to get everything set up.

### Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Create environment file

To make sure the code can access your secrets, run:

```
cp example.env .env
```

In the next steps we will populate the `.env` file with your API keys and credentials.

### Get OpenAI API Key

1. Go to [OpenAI's website](https://openai.com/) and create an account if you don't have one
2. Navigate to the [API Keys page](https://platform.openai.com/api-keys)
3. Click "Create new secret key"
4. Copy the key and add it to your `.env` file:
   ```
   OPENAI_API_KEY=your_key_here
   ```

### Get Anthropic API Key

1. Go to [Anthropic's website](https://www.anthropic.com/) and create an account if you don't have one
2. Navigate to the [API Keys page](https://console.anthropic.com/settings/keys)
3. Click "Create Key"
4. Copy the key and add it to your `.env` file:
   ```
   ANTHROPIC_API_KEY=your_key_here
   ```

### Get Lilypad API Key

1. Go to [Lilypad's website](https://lilypad.so/) and create an account if you don't have one
2. Navigate to your dashboard and find the API keys section
3. Generate a new API key
4. Copy the key and add it to your `.env` file:
   ```
   LILYPAD_API_KEY=your_key_here
   ```

### Get HumanLayer API Key

1. Go to [HumanLayer's website](https://humanlayer.dev/) and create an account if you don't have one
2. Navigate to your dashboard and find the API keys section
3. Generate a new API key
4. Copy the key and add it to your `.env` file:
   ```
   HUMANLAYER_API_KEY=your_key_here
   ```

### Install Browser MCP Extension

Note: requires Chrome browser

1. Navigate to [Browser MCP](https://browsermcp.io/)
2. Click the 'Add to Chrome' button
3. Pin the extension
4. Open the extension
5. Click 'Connect'

### Setup Gmail OAuth Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Desktop application" as the application type
   - Download the credentials JSON file
5. Save the credentials file to `.gmail-mcp/gcp-oauth.keys.json` in your home (`$HOME`) directory

## Example Usage

```bash
# run the server
uv run uvicorn automations.mymcp:sse_app --port 8082 --reload

# Trigger the weekly review
uv run automations/mymcp.py weekly_review
```
