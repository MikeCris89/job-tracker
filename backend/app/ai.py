import anthropic
from anthropic.types import TextBlock, ToolParam
from app.schemas import PostingExtraction

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


EXTRACTION_TOOL: ToolParam = {
    "name": "record_posting",
    "description": "Record the structured fields extracted from a job posting.",
    "input_schema": PostingExtraction.model_json_schema(),
}

SYSTEM_PROMPT = """You extract structured data from job postings.

Rules:
- Use the record_posting tool. Do not reply with prose.
- Only record what the posting actually states. If a field is not present, leave it null. Never guess or infer.
- summary: a condensed version of the ENTIRE posting, all information retained, just trimmed. Not a teaser.
- link: only if a URL appears literally in the text. Do not construct one.
"""

def extract_posting(raw_posting: str) -> PostingExtraction:
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        tools=[EXTRACTION_TOOL],
        tool_choice={"type": "tool", "name": "record_posting"},
        messages=[{"role": "user", "content": raw_posting}],
    )

    for block in message.content:
        if block.type == "tool_use":
            return PostingExtraction.model_validate(block.input)

    raise ValueError("Model did not call the extraction tool")