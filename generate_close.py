import asyncio
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

import config
from scraper.schedule_helper import is_run_day
from scraper.market_snapshot import get_market_snapshot
from scraper.naver_finance import get_domestic_close_headlines, get_article_text
from ai.close import generate_close_briefing
from render import render_html
from state import load_state, save_state


async def main():
    today = date.today()

    if not is_run_day(today):
        print("오늘은 주말이라 실행하지 않습니다.")
        return

    if not config.AI_SUMMARY_ENABLED:
        print("config.AI_SUMMARY_ENABLED가 꺼져있어 실행하지 않습니다.")
        return

    print("실시간 시세 수집 중...")
    snapshot = get_market_snapshot()
    print(snapshot)

    headlines = get_domestic_close_headlines(pages=5)[:8]
    articles = []
    for h in headlines:
        print("수집:", h["title"])
        text = get_article_text(h["link"])
        articles.append({"title": h["title"], "text": text})

    print("\nAI 분석 중...")
    close = await generate_close_briefing(snapshot, articles)

    state = load_state(today)
    state["close"] = close.model_dump()
    save_state(state)

    html = render_html(state, today)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("\n오늘 마감 코멘트에 담긴 흐름:")
    for topic in close.topics_covered:
        print(" -", topic)

    print("\nindex.html 생성 완료 (시장마감)")


if __name__ == "__main__":
    asyncio.run(main())
