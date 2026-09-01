from pydantic import BaseModel

from ai.client import ask_structured
from ai.sections import SECTIONS


class BriefingSection(BaseModel):
    title: str
    content: str


class MarketBriefing(BaseModel):
    sections: list[BriefingSection]


def _build_prompt(articles: list[dict]) -> str:
    article_block = "\n\n".join(
        f"[기사 {i+1}] {a['title']}\n{a['text']}"
        for i, a in enumerate(articles)
    )

    section_block = "\n".join(f"{i+1}. {s}" for i, s in enumerate(SECTIONS))

    return f"""당신은 국내 증권사의 리서치 담당자입니다.
아래는 오늘 아침 수집된 관련 기사 원문들입니다. 이 기사들을 바탕으로
국내증시 개장 전 시황 브리핑을 작성하세요.

반드시 아래 항목 순서와 개수에 맞춰 작성하고, 각 항목은 2~4문장 정도로
간결하게 정리하세요. 기사에 없는 내용은 추측하지 말고, 근거가 부족하면
"관련 정보 부족"이라고 명시하세요. title에는 "1.", "①" 같은 번호를
넣지 마세요 (화면에 표시할 때 번호가 자동으로 붙습니다).

[작성할 항목]
{section_block}

[수집된 기사 원문]
{article_block}
"""


async def generate_briefing(articles: list[dict]) -> MarketBriefing:
    prompt = _build_prompt(articles)
    return await ask_structured(prompt, MarketBriefing)
