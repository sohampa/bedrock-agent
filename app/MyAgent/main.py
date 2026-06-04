from typing import Any

from strands import Agent
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from model.load import load_model
from mcp_client.client import get_streamable_http_mcp_client
from review.payload import build_user_message, parse_review_payload
from review.prompts import CODE_REVIEW_SYSTEM_PROMPT
from review.scope import is_in_scope
from tools.github_tools import fetch_github_pr_diff, post_github_pr_review_comment

app = BedrockAgentCoreApp()
log = app.logger

mcp_clients = [get_streamable_http_mcp_client()]

tools: list[Any] = [
    fetch_github_pr_diff,
    post_github_pr_review_comment,
]

for mcp_client in mcp_clients:
    if mcp_client:
        tools.append(mcp_client)

_agent = None


def get_or_create_agent():
    global _agent
    if _agent is None:
        _agent = Agent(
            model=load_model(),
            system_prompt=CODE_REVIEW_SYSTEM_PROMPT,
            tools=tools,
        )
    return _agent


@app.entrypoint
async def invoke(payload, context):
    log.info("Invoking code review agent")

    data = parse_review_payload(payload if isinstance(payload, dict) else {"prompt": payload})

    allowed, denial = is_in_scope(data)
    if not allowed:
        log.info("Request denied: out of scope")
        yield denial or "Request is out of scope for this security review agent."
        return

    user_message = build_user_message(data)

    agent = get_or_create_agent()
    stream = agent.stream_async(user_message)

    async for event in stream:
        if "data" in event and isinstance(event["data"], str):
            yield event["data"]


if __name__ == "__main__":
    app.run()
