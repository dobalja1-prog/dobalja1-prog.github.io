import asyncio
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

import config
from scraper.schedule_helper import is_run_day, get_lookback_days
from scraper.naver_finance import get_us_market_headlines, get_article_text
from ai.summarizer import generate_briefing
from render import render_html
from state import load_state, save_state
from history import get_recent, add_entry


async def main():
    today = date.today()

    if not is_run_day(today):
        print("오늘은 주말이라 실행하지 않습니다.")
        return

    if not config.AI_SUMMARY_ENABLED:
        print("config.AI_SUMMARY_ENABLED가 꺼져있어 실행하지 않습니다.")
        return

    lookback = get_lookback_days(today)
    pages = 5 if lookback == 1 else 12  # 월요일엔 주말치까지 더 넓게 탐색
    print(f"조회 기간: {lookback}일치 / 탐색 페이지: {pages}")

    headlines = get_us_market_headlines(pages=pages)[:8]
    if not headlines:
        print("관련 기사를 찾지 못했습니다. 종료합니다.")
        return

    articles = []
    for h in headlines:
        print("수집:", h["title"])
        text = get_article_text(h["link"])
        articles.append({"title": h["title"], "text": text})

    recent_history = get_recent("morning", today.isoformat())

    print("\nAI 분석 중...")
    briefing = await generate_briefing(articles, today, recent_history)

    state = load_state(today)
    state["morning"] = briefing.model_dump()
    save_state(state)
    add_entry("morning", today.isoformat(), briefing.chat_summary)

    html = render_html(state, today)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("\nindex.html 생성 완료")


if __name__ == "__main__":
    asyncio.run(main())
