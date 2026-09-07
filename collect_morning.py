import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

from scraper.schedule_helper import is_run_day, get_lookback_days
from scraper.naver_finance import get_us_market_headlines, get_article_text
from ai.summarizer import _build_prompt
from history import get_recent

OUTPUT_DIR = "수집자료"


def main():
    today = date.today()
    output_path = f"{OUTPUT_DIR}/[{today.strftime('%Y.%m.%d')} 오전브리핑].txt"

    if not is_run_day(today):
        print("오늘은 주말이라 실행하지 않습니다.")
        return

    lookback = get_lookback_days(today)
    pages = 5 if lookback == 1 else 12
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
    prompt = _build_prompt(articles, today, recent_history)
    prompt += (
        "\n\n[최종 출력]\n"
        "위 내용을 참고해서 chat_summary에 해당하는, 단체방에 바로 붙여넣을 수 있는 "
        "하나의 자연스러운 글만 작성해줘. headline/sentiment/key_stats/sections 같은 "
        "다른 항목은 만들 필요 없어."
    )

    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"\n완료: {output_path} 에 저장됨. 이 파일 내용을 GPT에 복붙하세요.")


if __name__ == "__main__":
    main()
