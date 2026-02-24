import sys
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

query = sys.argv[1]

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": query}],
)

print(response.content[0].text)
