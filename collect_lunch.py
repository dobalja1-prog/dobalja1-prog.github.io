import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

from scraper.schedule_helper import is_run_day
from scraper.market_snapshot import get_market_snapshot
from ai.lunch import _build_prompt
from history import get_recent

OUTPUT_PATH = "for_gpt/lunch.txt"


def main():
    today = date.today()

    if not is_run_day(today):
        print("오늘은 주말이라 실행하지 않습니다.")
        return

    print("실시간 시세 수집 중...")
    snapshot = get_market_snapshot()
    print(snapshot)

    recent_history = get_recent("lunch", today.isoformat())
    prompt = _build_prompt(snapshot, today, recent_history)
    prompt += (
        "\n\n[최종 출력]\n"
        "위 내용을 참고해서 단체방에 바로 붙여넣을 수 있는 하나의 자연스러운 "
        "점심시간 브리핑 글만 작성해줘."
    )

    import os
    os.makedirs("for_gpt", exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"\n완료: {OUTPUT_PATH} 에 저장됨. 이 파일 내용을 GPT에 복붙하세요.")


if __name__ == "__main__":
    main()
