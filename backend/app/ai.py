import base64
import anthropic
from anthropic.types import TextBlock, ToolParam
from app.schemas import CVExtraction, PostingExtraction

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

POSTING_SYSTEM_PROMPT = """You extract structured data from job postings.

Rules:
- Use the record_posting tool. Do not reply with prose.
- Only record what the posting actually states. If a field is not present, leave it null. Never guess or infer.
- summary: a condensed version of the ENTIRE posting, all information retained, just trimmed. Not a teaser.
- link: only if a URL appears literally in the text. Do not construct one.
"""

CV_SYSTEM_PROMPT = """You extract the technologies from a candidate's CV.

Rules:
- Use the record_cv_skills tool. Do not reply with prose.
- Only record technologies the CV actually names. Never guess or infer a skill from a job title or company.
- Record a technology once, even if it appears in multiple roles.
"""

def extract_posting(raw_posting: str) -> PostingExtraction:
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=POSTING_SYSTEM_PROMPT,
        tools=[EXTRACTION_TOOL],
        tool_choice={"type": "tool", "name": "record_posting"},
        messages=[{"role": "user", "content": raw_posting}],
    )

    for block in message.content:
        if block.type == "tool_use":
            return PostingExtraction.model_validate(block.input)

    raise ValueError("Model did not call the extraction tool")


def extract_cv_text(raw: bytes, content_type: str | None) -> str:
    if content_type == "text/plain":
        return raw.decode("utf-8")
    if content_type == "application/pdf":
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "document", "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": base64.standard_b64encode(raw).decode(),
                    }},
                    {"type": "text", "text": "Output the full text of this CV in reading order. No preamble, no commentary."},
                ],
            }],
        )
        return extract_text(message) 
    raise ValueError(f"Unsupported content type: {content_type}")

CV_TOOL: ToolParam = {
    "name": "record_cv_skills",
    "description": "Record the technologies found in a CV.",
    "input_schema": CVExtraction.model_json_schema(),
}

def extract_cv_skills(cv: str) -> list[str]:
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=CV_SYSTEM_PROMPT,          # your existing global one
        tools=[CV_TOOL],
        tool_choice={"type": "tool", "name": "record_cv_skills"},
        messages=[{"role": "user", "content": cv}],
    )
    for block in message.content:
        if block.type == "tool_use":
            return CVExtraction.model_validate(block.input).skills
    raise ValueError("Model did not call the extraction tool")