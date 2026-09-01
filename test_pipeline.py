import asyncio
import sys

sys.stdout.reconfigure(encoding="utf-8")

from scraper.naver_finance import get_us_market_headlines, get_article_text
from ai.summarizer import generate_briefing


async def main():
    headlines = get_us_market_headlines(pages=5)[:5]
    articles = []
    for h in headlines:
        text = get_article_text(h["link"])
        articles.append({"title": h["title"], "text": text})
        print("수집:", h["title"])

    print("\nAI 분석 중...\n")
    briefing = await generate_briefing(articles)

    for section in briefing.sections:
        print(f"## {section.title}")
        print(section.content)
        print()


asyncio.run(main())
