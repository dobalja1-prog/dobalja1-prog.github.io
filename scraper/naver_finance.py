import re
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

LIST_URL_BASE = "https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101"

# section_id2: 262=해외증시, 258=국내(증권 일반) 뉴스
SECTION_OVERSEAS = 262
SECTION_DOMESTIC = 258

# 미국 증시 마감 관련 기사를 골라내는 키워드.
# '해외증시' 목록에는 중국/일본/유럽 등 다른 뉴스도 섞여있어서,
# 카테고리가 아니라 제목 키워드로 걸러내는 게 더 안정적이다.
US_MARKET_KEYWORDS = ["다우", "나스닥", "S&P", "뉴욕증시", "뉴욕 증시", "뉴욕마켓", "뉴욕 마켓"]

# 국내증시 마감/특징주 관련 기사를 골라내는 키워드.
DOMESTIC_CLOSE_KEYWORDS = ["마감", "특징주", "코스피", "코스닥"]


def get_headline_list(pages=1, section_id2=SECTION_OVERSEAS):
    """네이버 금융 뉴스 목록에서 (제목, 링크) 목록을 가져온다.

    pages를 늘리면 더 과거(더 아래) 기사까지 가져온다.
    """
    results = []
    for page in range(1, pages + 1):
        url = f"{LIST_URL_BASE}&section_id2={section_id2}"
        response = requests.get(url, params={"page": page}, headers=HEADERS)
        response.encoding = "euc-kr"
        soup = BeautifulSoup(response.text, "html.parser")

        for a in soup.select("dl > dd.articleSubject > a"):
            title = a.get_text(strip=True)
            ids = re.search(r"article_id=(\d+).*?office_id=(\d+)", a["href"])
            if not ids:
                continue
            article_id, office_id = ids.group(1), ids.group(2)
            link = f"https://n.news.naver.com/mnews/article/{office_id}/{article_id}"
            results.append({"title": title, "link": link})
    return results


def filter_us_market_news(headlines):
    """제목에 미국 증시 관련 키워드가 있는 기사만 남긴다."""
    return [h for h in headlines if any(k in h["title"] for k in US_MARKET_KEYWORDS)]


def get_us_market_headlines(pages=5):
    """여러 페이지를 뒤져서 미국 증시 마감 관련 기사만 뽑아온다."""
    return filter_us_market_news(get_headline_list(pages=pages, section_id2=SECTION_OVERSEAS))


def get_domestic_close_headlines(pages=5):
    """국내증시 마감/특징주 관련 기사를 뽑아온다."""
    headlines = get_headline_list(pages=pages, section_id2=SECTION_DOMESTIC)
    return [h for h in headlines if any(k in h["title"] for k in DOMESTIC_CLOSE_KEYWORDS)]


def get_article_text(link):
    """네이버 뉴스 기사 본문 텍스트를 가져온다."""
    response = requests.get(link, headers=HEADERS)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    body = soup.select_one("#dic_area")
    if not body:
        return ""
    return body.get_text(separator="\n", strip=True)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")

    headlines = get_headline_list()
    for item in headlines[:3]:
        print("제목:", item["title"])
        text = get_article_text(item["link"])
        print("본문 앞부분:", text[:150])
        print("=" * 40)
