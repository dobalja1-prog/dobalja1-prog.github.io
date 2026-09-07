"""해외 지수, 환율/원자재, 개별 종목 시세를 네이버의 비공식 API/페이지에서 가져온다."""

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# (네이버 지수 코드, 표시 이름)
WORLD_INDEX_CODES = [
    (".DJI", "다우존스"),
    (".IXIC", "나스닥종합"),
    (".INX", "S&P500"),
    (".SOX", "필라델피아반도체(SOX)"),
    (".VIX", "VIX(공포지수)"),
]

# finance.naver.com/marketindex/ 페이지의 label -> 표시 이름.
# (원화 환산 환율은 exchangeList, 해외 환율/원자재는 worldExchangeList・oilGoldList에 있다)
FOREX_COMMODITY_LABELS = {
    "미국 USD": "원/달러",
    "일본 JPY(100엔)": "원/엔(100엔)",
    "유럽연합 EUR": "원/유로",
    "중국 CNY": "원/위안",
    "달러/일본 엔": "달러/엔",
    "달러인덱스": "달러인덱스",
    "WTI": "WTI",
    "국제 금": "국제 금",
}


def get_world_indices():
    """다우/나스닥/S&P500/SOX/VIX 실시간(또는 최근 마감) 값을 가져온다."""
    result = []
    for code, label in WORLD_INDEX_CODES:
        response = requests.get(
            f"https://api.stock.naver.com/index/{code}/basic", headers=HEADERS, timeout=10
        )
        d = response.json()
        result.append(
            {
                "label": label,
                "current": d.get("closePrice"),
                "change": d.get("compareToPreviousClosePrice"),
                "change_pct": d.get("fluctuationsRatio"),
                "direction": d.get("compareToPreviousPrice", {}).get("text"),
            }
        )
    return result


def get_stock_quote(code):
    """개별 종목(예: 삼성전자 005930)의 현재가/등락을 가져온다."""
    response = requests.get(
        f"https://m.stock.naver.com/api/stock/{code}/basic", headers=HEADERS, timeout=10
    )
    d = response.json()
    return {
        "name": d.get("stockName"),
        "current": d.get("closePrice"),
        "change": d.get("compareToPreviousClosePrice"),
        "change_pct": d.get("fluctuationsRatio"),
        "direction": d.get("compareToPreviousPrice", {}).get("text"),
    }


def _parse_market_index_list(ul):
    items = {}
    if not ul:
        return items
    for li in ul.select("li"):
        label_el = li.select_one("h3.h_lst .blind")
        value_el = li.select_one(".value")
        change_el = li.select_one(".change")
        if not label_el or not value_el:
            continue
        direction_el = change_el.find_next_sibling("span", class_="blind") if change_el else None
        items[label_el.get_text(strip=True)] = {
            "value": value_el.get_text(strip=True),
            "change": change_el.get_text(strip=True) if change_el else None,
            "direction": direction_el.get_text(strip=True) if direction_el else None,
        }
    return items


def get_forex_commodities():
    """원/달러, 원/엔, 달러인덱스, WTI, 국제 금 등 주요 환율·원자재를 가져온다."""
    response = requests.get("https://finance.naver.com/marketindex/", headers=HEADERS)
    response.encoding = "euc-kr"
    soup = BeautifulSoup(response.text, "html.parser")

    raw = {}
    for list_id in ["exchangeList", "worldExchangeList", "oilGoldList"]:
        raw.update(_parse_market_index_list(soup.select_one(f"#{list_id}")))

    result = []
    for raw_label, display_label in FOREX_COMMODITY_LABELS.items():
        item = raw.get(raw_label)
        if item:
            result.append({"label": display_label, **item})
    return result
