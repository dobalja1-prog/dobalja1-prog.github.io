import html as html_lib


def _escape(text: str) -> str:
    return html_lib.escape(text).replace("\n", "<br>")


def render_html(briefing, generated_date) -> str:
    date_str = generated_date.strftime("%Y년 %m월 %d일")
    weekday_kr = ["월", "화", "수", "목", "금", "토", "일"][generated_date.weekday()]

    sections_html = "\n".join(
        f"""
        <section class="card">
          <h2><span class="num">{i+1}</span>{_escape(s.title)}</h2>
          <p>{_escape(s.content)}</p>
        </section>"""
        for i, s in enumerate(briefing.sections)
    )

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>오늘의 시황 브리핑</title>
<style>
  :root {{
    --bg: #f5f6f8;
    --card-bg: #ffffff;
    --text: #1a1c1e;
    --sub: #6b7280;
    --accent: #2563eb;
    --border: #e5e7eb;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 32px 16px 64px;
    background: var(--bg);
    color: var(--text);
    font-family: "Pretendard", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
    line-height: 1.65;
  }}
  header {{
    max-width: 720px;
    margin: 0 auto 24px;
  }}
  header h1 {{
    font-size: 1.6rem;
    margin: 0 0 4px;
  }}
  header p {{
    color: var(--sub);
    margin: 0;
    font-size: 0.95rem;
  }}
  main {{
    max-width: 720px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }}
  .card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 22px;
  }}
  .card h2 {{
    font-size: 1.05rem;
    margin: 0 0 10px;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .num {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: var(--accent);
    color: white;
    font-size: 0.75rem;
    flex-shrink: 0;
  }}
  .card p {{
    margin: 0;
    font-size: 0.95rem;
    color: #333;
  }}
  footer {{
    max-width: 720px;
    margin: 32px auto 0;
    color: var(--sub);
    font-size: 0.8rem;
    text-align: center;
  }}
</style>
</head>
<body>
  <header>
    <h1>오늘의 시황 브리핑</h1>
    <p>{date_str} ({weekday_kr}) · 개장 전 요약</p>
  </header>
  <main>
    {sections_html}
  </main>
  <footer>
    이 페이지는 매일 아침 자동으로 수집·생성됩니다. 투자 판단의 참고용이며, 투자 조언이 아닙니다.
  </footer>
</body>
</html>
"""
