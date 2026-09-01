import sys
import re
import requests
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")

URL = "https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=262"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

response = requests.get(URL, headers=headers)
response.encoding = "euc-kr"
print("응답 코드:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

articles = soup.select("dl > dd.articleSubject > a")

for a in articles[:10]:
    title = a.get_text(strip=True)
    ids = re.search(r"article_id=(\d+).*?office_id=(\d+)", a["href"])
    article_id, office_id = ids.group(1), ids.group(2)
    link = f"https://finance.naver.com/news/news_read.naver?article_id={article_id}&office_id={office_id}"
    print(title)
    print(link)
    print("---")
