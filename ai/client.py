"""
claude-agent-sdk 래퍼.

claude-agent-sdk는 로컬에 설치된 claude CLI를 서브프로세스로 구동한다.
CLI가 `claude login`으로 구독(Pro/Max) 세션을 갖고 있고 환경변수
ANTHROPIC_API_KEY가 설정되어 있지 않다면, 그 구독 세션을 그대로 물려받아
사용한다 (API 비용 없음, 구독 사용량에서 차감).
"""

from typing import TypeVar

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query
from pydantic import BaseModel

from config import CLAUDE_MODEL

T = TypeVar("T", bound=BaseModel)


class ClaudeQueryError(Exception):
    pass


async def ask_structured(prompt: str, schema_model: type[T]) -> T:
    """schema_model에 맞는 JSON 응답을 요청하고 파싱된 pydantic 객체로 반환."""
    options = ClaudeAgentOptions(
        model=CLAUDE_MODEL,
        output_format={"type": "json_schema", "schema": schema_model.model_json_schema()},
    )

    result: ResultMessage | None = None
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, ResultMessage):
            result = message

    if result is None:
        raise ClaudeQueryError(
            "Claude로부터 응답을 받지 못했습니다. claude CLI가 로그인되어 있는지 확인하세요 (claude login)."
        )
    if result.is_error:
        raise ClaudeQueryError(f"Claude 호출 오류: {result.result or result.subtype}")

    data = result.structured_output
    if data is None:
        raise ClaudeQueryError("구조화된 응답을 받지 못했습니다.")

    return schema_model.model_validate(data)
