from mirascope import llm, Messages
from mirascope.mcp import sse_client
import lilypad
from automations.config import SERVER_URL
from pydantic import BaseModel, Field, ValidationError
from tenacity import retry, stop_after_attempt


class LinkedInAnalytics(BaseModel):
    num_followers: int = Field(description="The number of followers you have on LinkedIn")
    num_followers_growth_pct_7d: float = Field(description="The percentage growth in followers you have on LinkedIn")
    num_impressions_7d: int = Field(description="The number of impressions you have on LinkedIn")
    num_profile_viewers_7d: int = Field(description="The number of profile viewers you have on LinkedIn")
    num_posts_7d: int = Field(description="The number of posts you have on LinkedIn")
    num_comments_7d: int = Field(description="The number of comments you have on LinkedIn")
    num_search_appearances_7d: int = Field(description="The number of search appearances you have on LinkedIn")


@lilypad.trace(versioning='automatic')
@llm.call(provider="anthropic", model="claude-sonnet-4-20250514", response_model=LinkedInAnalytics)
async def get_linkedin_analytics(*, history: list[Messages.Type] | None = None) -> list[Messages.Type]:
    history = history or []
    return [
        Messages.System("You are a helpful assistant that can navigate the web. You specialize in getting LinkedIn analytics. Navigate to https://www.linkedin.com/dashboard/ and extract out the relevant metrics."),
        Messages.User("Please visit linkedin.com and get the analytics for the current page"),
        *history,
    ]

async def run_browser_task_one_step_(task, *args, history: list[Messages.Type], **kwargs):
    try:
        result = await task(*args, history=history, **kwargs)
    except ValidationError as e:
        print(f'Validation error with {task.__name__}: {e}')
        history.append(Messages.User(f'Could you try again? It seems like you made a mistake, here is the error: {e}'))
        return None, history, False
    if tools := getattr(result, 'tools', None):
        tools_and_outputs = []
        for tool in tools:
            try:
                tool_result = await retry(stop=stop_after_attempt(2), before=lambda x: print(f'Trying tool {tool._name()} ({x.attempt_number} / 2)'))(tool.call)()
            except Exception as e:
                print(f'Error calling tool {tool._name()}: {e}')
                tool_result = f'Error calling tool {tool._name()}. Maybe you do not need this tool call: {e}'
            tools_and_outputs.append((tool, tool_result))
        if tools_and_outputs:
            history.append(result.message_param)
            history += result.tool_message_params(tools_and_outputs)
        return result, history, False
    return result, history, True


@lilypad.trace(versioning='automatic')
async def run_browser_task(task, *args, **kwargs):
    async with sse_client(SERVER_URL) as client:
        tools = await client.list_tools()
        browser_tools = [t for t in tools if t._name().startswith("Browser")]
        print(f'Found {len(browser_tools)} browser tools')
        task_fn = llm.override(task, tools=browser_tools)
        history = []
        done = False
        step = 0
        while not done:
            step += 1
            if step > 10:
                raise Exception('Browser task took too long to complete')
            result, history, done = await run_browser_task_one_step_(task_fn, *args, history=history, **kwargs)
        return result

