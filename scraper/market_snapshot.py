"""네이버페이 증권의 비공식 모바일 API로 실시간 국내 지수 스냅샷을 가져온다.

- /api/index/{code}/basic      : 현재가, 등락률, 거래량 등
- /api/index/{code}/integration: 투자자별 순매수, 상승/하락 종목수(ADR) 등
"""

import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def _get_json(url):
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response.json()


def get_index_snapshot(code):
    """code: "KOSPI" 또는 "KOSDAQ". 지수/수급/등락종목수를 하나로 묶어 반환."""
    basic = _get_json(f"https://m.stock.naver.com/api/index/{code}/basic")
    integ = _get_json(f"https://m.stock.naver.com/api/index/{code}/integration")

    deal = integ.get("dealTrendInfo", {})
    updown = integ.get("upDownStockInfo", {})

    return {
        "name": basic.get("stockName"),
        "current": basic.get("closePrice"),
        "change": basic.get("compareToPreviousClosePrice"),
        "change_direction": basic.get("compareToPreviousPrice", {}).get("text"),
        "change_pct": basic.get("fluctuationsRatio"),
        "open": basic.get("openPrice"),
        "high": basic.get("highPrice"),
        "low": basic.get("lowPrice"),
        "market_status": basic.get("marketStatus"),
        "foreign_net": deal.get("foreignValue"),
        "institution_net": deal.get("institutionalValue"),
        "personal_net": deal.get("personalValue"),
        "rise_count": updown.get("riseCount"),
        "fall_count": updown.get("fallCount"),
        "steady_count": updown.get("steadyCount"),
        "upper_limit_count": updown.get("upperCount"),
        "lower_limit_count": updown.get("lowerCount"),
    }


def get_market_snapshot():
    """코스피, 코스닥 스냅샷을 함께 반환."""
    return {
        "kospi": get_index_snapshot("KOSPI"),
        "kosdaq": get_index_snapshot("KOSDAQ"),
    }


if __name__ == "__main__":
    import sys
    import json

    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(get_market_snapshot(), indent=2, ensure_ascii=False))
