import asyncio
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

import config
from scraper.schedule_helper import is_run_day
from scraper.market_snapshot import get_market_snapshot
from ai.lunch import generate_lunch_briefing
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

    print("실시간 시세 수집 중...")
    snapshot = get_market_snapshot()
    print(snapshot)

    recent_history = get_recent("lunch", today.isoformat())

    print("\nAI 분석 중...")
    lunch = await generate_lunch_briefing(snapshot, today, recent_history)

    state = load_state(today)
    state["lunch"] = lunch.model_dump()
    save_state(state)
    add_entry("lunch", today.isoformat(), lunch.text)

    html = render_html(state, today)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("\nindex.html 생성 완료 (점심시간)")


if __name__ == "__main__":
    asyncio.run(main())
