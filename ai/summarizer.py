from pydantic import BaseModel

from ai.client import ask_structured
from ai.sections import SECTIONS


class BriefingSection(BaseModel):
    title: str
    content: str


class KeyStat(BaseModel):
    label: str  # 예: "다우", "나스닥", "코스피"
    value: str  # 예: "53,185.90"
    change: str  # 예: "-0.70%" (부호를 반드시 포함)


class MarketBriefing(BaseModel):
    headline: str  # 오늘 시황을 한 문장으로 요약
    sentiment: str  # "상승" | "하락" | "혼조" 중 하나
    key_stats: list[KeyStat]
    sections: list[BriefingSection]


def _build_prompt(articles: list[dict]) -> str:
    article_block = "\n\n".join(
        f"[기사 {i+1}] {a['title']}\n{a['text']}"
        for i, a in enumerate(articles)
    )

    section_block = "\n".join(f"{i+1}. {s}" for i, s in enumerate(SECTIONS))

    return f"""당신은 국내 증권사의 리서치 담당자입니다.
아래는 오늘 아침 수집된 관련 기사 원문들입니다. 이 기사들을 바탕으로
국내증시 개장 전 시황 브리핑을 본인이 직접 작성하는 것처럼 쓰세요.

[중요 - 문체]
- "연합인포맥스", "로이터", "AP", "블룸버그", "OO통신", "OO에 따르면" 같은
  언론사/통신사 이름이나 출처 표현은 절대 쓰지 마세요. 여러 기사를 짜깁기한
  게 아니라, 본인이 직접 분석해서 쓴 브리핑처럼 자연스럽게 서술하세요.
- 숫자·사실관계는 정확히 유지하되, 문장은 스스로 재구성하세요.
- "-했다", "-였다", "-이었다" 같은 딱딱한 기사체(신문 기사, 개조식) 어미는
  쓰지 마세요.
- 문장을 끝맺을 때(마침표 앞)는 반드시 "-습니다" 체를 쓰세요.
  "-했어요", "-됐어요", "-네요" 처럼 캐주얼한 "-요"체로 문장을 끝내지
  마세요.
- 다만 문장 중간에는 "-했고,", "-됐고,", "-하고요," 같은 자연스러운
  구어체 연결어미를 적절히 섞어서, 딱딱하게 나열만 하는 느낌이 들지
  않게 하세요. 즉 문장 중간의 연결은 사람처럼 자연스럽게, 문장을
  끝맺을 때는 "-습니다"체로 정리하는 식입니다.

[작성할 것]
- headline: 오늘 시황 전체를 한 문장으로 요약
- sentiment: "상승" / "하락" / "혼조" 중 하나만
- key_stats: 기사에 나온 주요 지수(다우, 나스닥, S&P500, 코스피 등)의
  수치와 등락률을 최대 5개까지. change는 반드시 +/- 부호 포함
  (예: "-0.70%", "+0.46%")
- sections: 아래 항목 순서와 개수에 맞춰 각 2~4문장으로 작성. 기사에 없는
  내용은 추측하지 말고 근거가 부족하면 "관련 정보 부족"이라고 명시.
  title에는 "1.", "①" 같은 번호를 넣지 마세요.

[작성할 항목]
{section_block}

[수집된 기사 원문]
{article_block}
"""


async def generate_briefing(articles: list[dict]) -> MarketBriefing:
    prompt = _build_prompt(articles)
    return await ask_structured(prompt, MarketBriefing)
