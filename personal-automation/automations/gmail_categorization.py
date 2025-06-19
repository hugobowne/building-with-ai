from mirascope import llm, prompt_template
from mirascope.core import FromCallArgs
from pydantic import BaseModel, Field, model_validator, ValidationError
from typing import Literal, Annotated
from automations.gmail_types import GmailThreadHeader
from mirascope.retries.tenacity import collect_errors
from tenacity import retry, stop_after_attempt
from automations.decorators import batch, hitl_validation, self_consistency
import lilypad
from collections import defaultdict


class GmailClassification(BaseModel):
    reason: str = Field(description="The reason for the classification.")
    classification: Literal["draft_reply", "archive"] = Field(description="The classification of the email.")

class GmailClassificationResponse(BaseModel):
    emails: Annotated[list[GmailThreadHeader], FromCallArgs()]
    thinking: str = Field(description="The thinking process of the LLM. Think as much as you need to.")
    classifications: list[GmailClassification] = Field(description="The classifications of the emails.")

    @model_validator(mode="after")
    def validate_classifications(self):
        if len(self.classifications) != len(self.emails):
            raise ValueError(f"The number of classifications ({len(self.classifications)}) must match the number of emails ({len(self.emails)}).")
        return self



_PROMPT_TEMPLATE = """SYSTEM: You are an expert personal assistant. You know exactly how to spend the minimum amount of time on each email while still
providing a high quality work.

For each email, you can take one of the following actions:

- draft a reply
- archive the email

- You should draft a reply on emails that likely have a human on the other end
- You should archive emails that are largely just informational
- Reminder emails are always archived (even for booked meetings)
- If I have already replied to the email (me@skylarbpayne.com), you should archive the email

USER:
Please categorize the following emails:

<emails>
{emails_rendered}
</emails>

Output exactly {num_emails} classifications, in the order corresponding to the emails.

You encountered the following errors with your previous attempts. Please use this information to improve your next attempt.

<errors>
{errors}
</errors>

<prev_result>
{prev_result}
</prev_result>

<feedback>
{feedback}
</feedback>
"""

def _gmail_reduce_fn(a: GmailClassificationResponse, b: GmailClassificationResponse) -> GmailClassificationResponse:
    """Custom reduce function for combining Gmail classification batches."""
    return GmailClassificationResponse(
        emails=a.emails + b.emails,
        thinking=a.thinking + "\n\n" + b.thinking,
        classifications=a.classifications + b.classifications
    )

def _gmail_aggregate_fn(responses: list[GmailClassificationResponse]) -> GmailClassificationResponse:
    votes = [defaultdict(int) for _ in responses[0].classifications]
    for r in responses:
        for i, c in enumerate(r.classifications):
            votes[i][c.classification] += 1
    
    return GmailClassificationResponse(
        emails=responses[0].emails,
        thinking=responses[0].thinking,
        classifications=[next(r.classifications[i] for r in responses 
                             if r.classifications[i].classification == max(v, key=v.get))
                        for i, v in enumerate(votes)]
    )

@lilypad.trace(versioning='automatic')
@batch(batch_size=7, reduce_fn=_gmail_reduce_fn)
@hitl_validation(max_steps=2)
@self_consistency(k=3, aggregate_fn=_gmail_aggregate_fn)
@retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError), reraise=True)
@llm.call(provider="openai", model="gpt-4o-mini", response_model=GmailClassificationResponse)
@prompt_template(_PROMPT_TEMPLATE)
def categorize_gmail_emails(
    emails: list[GmailThreadHeader], 
    *, 
    errors: list[ValidationError] | None = None,
    prev_result: GmailClassificationResponse | None = None,
    feedback: str | None = None
):
    """Gmail classification with human approval workflow."""
    
    return {
        "computed_fields": {
            "num_emails": len(emails),
            "emails_rendered": "\n---\n".join([email.model_dump_json(indent=2) for email in emails]),
        }
    }


@lilypad.trace(versioning='automatic')
@llm.call(provider="openai", model="gpt-4o-mini")
@prompt_template("""SYSTEM: You are an expert personal assistant. You write draft emails that I may later edit.
                 
<instructions>
- your response should be concise and to the point, do not belabor any point over and over
- you should write from the perspective of what the sender ultimately wants to achieve; lead with their problems
- use simple, 6th grade level language
- vary the rhythm of sentences to keep the reader engaged
</instructions>

USER: Please write a draft response to the following email:

<thread>
{thread}
</thread>

Remember your instructions.
""")
async def draft_reply(content: str): ...
