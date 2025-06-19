from pydantic import BaseModel, Field


class GmailThreadHeader(BaseModel):
    id: str = Field(description="The ID of the email thread.")
    snippet: str = Field(description="The snippet of the email containing like subject and some email content")
    historyId: str = Field(description="The history ID of the email thread.")