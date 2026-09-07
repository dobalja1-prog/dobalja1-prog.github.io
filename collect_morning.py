import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

from scraper.schedule_helper import is_run_day, get_lookback_days
from scraper.naver_finance import get_us_market_headlines, get_article_detail
from scraper.world_market import get_world_indices, get_forex_commodities, get_stock_quote
from scraper.market_snapshot import get_market_snapshot
from ai.lunch import _format_snapshot

OUTPUT_DIR = "수집자료"

FEATURED_STOCKS = [("005930", "삼성전자"), ("000660", "SK하이닉스")]

MIN_ARTICLE_LENGTH = 80  # 이보다 짧으면 광고/스텁성 기사로 보고 제외


def _format_index_line(item):
    change = str(item["change"]).lstrip("-")
    change_pct = str(item["change_pct"]).lstrip("-")
    return f"{item['label']}: {item['current']} ({item['direction']} {change}, {change_pct}%)"


def _format_forex_line(item):
    return f"{item['label']}: {item['value']} ({item['direction']} {item['change']})"


def _format_stock_line(item):
    return f"{item['name']}: {item['current']}원 ({item['direction']} {item['change_pct']}%)"


def main():
    today = date.today()
    output_path = f"{OUTPUT_DIR}/[{today.strftime('%Y.%m.%d')} 오전브리핑].txt"

    if not is_run_day(today):
        print("오늘은 주말이라 실행하지 않습니다.")
        return

    print("해외 지수 수집 중...")
    world_indices = get_world_indices()

    print("환율/원자재 수집 중...")
    forex_commodities = get_forex_commodities()

    print("국내 증시 스냅샷 수집 중...")
    snapshot = get_market_snapshot()

    print("특징주 시세 수집 중...")
    featured_stocks = []
    for code, name in FEATURED_STOCKS:
        try:
            featured_stocks.append(get_stock_quote(code))
        except Exception as e:
            print(f"{name} 시세 수집 실패:", e)

    lookback = get_lookback_days(today)
    pages = 5 if lookback == 1 else 12
    print(f"뉴스 조회 기간: {lookback}일치 / 탐색 페이지: {pages}")

    headlines = get_us_market_headlines(pages=pages)[:8]
    articles = []
    for h in headlines:
        detail = get_article_detail(h["link"])
        if len(detail["text"]) < MIN_ARTICLE_LENGTH:
            print("제외(본문 부족):", h["title"])
            continue
        print("수집:", h["title"])
        articles.append({"title": h["title"], **detail})

    lines = [f"[{today.strftime('%Y.%m.%d')} 오전 수집자료]\n"]

    lines.append("[미국 증시]")
    lines.extend(_format_index_line(i) for i in world_indices)
    lines.append("")

    lines.append("[국내 증시] (전일 마감 기준)")
    lines.append(_format_snapshot(snapshot))
    lines.append("")

    lines.append("[환율/원자재]")
    lines.extend(_format_forex_line(i) for i in forex_commodities)
    lines.append("")

    lines.append("[특징주/반도체]")
    lines.extend(_format_stock_line(i) for i in featured_stocks)
    lines.append("")

    lines.append("[주요 뉴스]")
    if not articles:
        lines.append("(수집된 기사 없음)")
    for i, a in enumerate(articles, 1):
        meta = " / ".join(filter(None, [a.get("press"), a.get("time")]))
        lines.append(f"[기사 {i}] {a['title']}" + (f" ({meta})" if meta else ""))
        lines.append(a["text"])
        lines.append("")

    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n완료: {output_path} 에 저장됨. 이 파일 내용을 GPT에 복붙하세요.")


if __name__ == "__main__":
    main()
