import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

from scraper.schedule_helper import is_run_day, get_lookback_days
from scraper.naver_finance import get_us_market_headlines, get_article_text

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

    lines = [f"[{today.strftime('%Y.%m.%d')} 오전 수집자료 - 미국 증시 관련 기사]\n"]
    for i, a in enumerate(articles, 1):
        lines.append(f"[기사 {i}] {a['title']}\n{a['text']}\n")

    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n완료: {output_path} 에 저장됨. 이 파일 내용을 GPT에 복붙하세요.")


if __name__ == "__main__":
    main()
