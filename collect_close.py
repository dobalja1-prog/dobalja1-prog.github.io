import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

from scraper.schedule_helper import is_run_day
from scraper.market_snapshot import get_market_snapshot
from scraper.naver_finance import get_domestic_close_headlines, get_article_text
from ai.close import _format_snapshot

OUTPUT_DIR = "수집자료"


def main():
    today = date.today()
    output_path = f"{OUTPUT_DIR}/[{today.strftime('%Y.%m.%d')} 마감브리핑].txt"

    if not is_run_day(today):
        print("오늘은 주말이라 실행하지 않습니다.")
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

    lines = [
        f"[{today.strftime('%Y.%m.%d')} 마감 수집자료 - 국내 증시 스냅샷 + 관련 기사]\n",
        f"[시장 스냅샷]\n{_format_snapshot(snapshot)}\n",
    ]
    for i, a in enumerate(articles, 1):
        lines.append(f"[기사 {i}] {a['title']}\n{a['text']}\n")

    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n완료: {output_path} 에 저장됨. 이 파일 내용을 GPT에 복붙하세요.")


if __name__ == "__main__":
    main()
