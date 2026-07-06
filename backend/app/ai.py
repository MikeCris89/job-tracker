import anthropic
from anthropic.types import TextBlock

client = anthropic.Anthropic()

def extract_text(message) -> str:
    block = message.content[0]
    if isinstance(block, TextBlock):
        return block.text
    raise ValueError(f"Expected text block, got {type(block).__name__}")

def smoke_test():
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=50,
        messages=[{"role": "user", "content": "Reply with exactly: pong"}],
    )
    print(extract_text(message))