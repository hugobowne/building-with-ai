from pydantic import BaseModel, Field


class GmailThreadHeader(BaseModel):
    id: str = Field(description="The ID of the email thread.")
    snippet: str = Field(description="The snippet of the email containing like subject and some email content")
    historyId: str = Field(description="The history ID of the email thread.")


class GmailThread(BaseModel):
    id: str = Field(description="The ID of the email thread.")
    reply_email: str = Field(description="The email address of the last sender.")
    reply_subject: str = Field(description="The subject of the email.")
    reply_content: str = Field(description="The content of the email as simple text.")