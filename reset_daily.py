import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

from scraper.schedule_helper import is_run_day
from render import render_html
from state import save_state


def main():
    today = date.today()

    if not is_run_day(today):
        print("오늘은 주말이라 실행하지 않습니다.")
        return

    state = {"date": today.isoformat(), "morning": None, "lunch": None, "close": None}
    save_state(state)

    html = render_html(state, today)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("초기화 완료 (오늘 브리핑 준비중 상태로 리셋)")


if __name__ == "__main__":
    main()
