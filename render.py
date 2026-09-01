import html as html_lib
import re

from ai.sections import SECTIONS
from ai.summarizer import MarketBriefing
from ai.lunch import LunchBriefing
from ai.close import CloseBriefing


# 문장 종결 어미: "-습니다.", "-입니다.", "-이죠.", "-했죠." 등
_SENTENCE_END = r"(?:다|죠)\."


def _escape(text: str) -> str:
    # 문장이 위 종결 어미로 끝날 때마다 줄바꿈을 넣어, 한 문단이 길게
    # 이어붙는 대신 문장 단위로 읽기 편하게 만든다.
    text = re.sub(rf"({_SENTENCE_END})(\s+)", r"\1\n", text)
    return html_lib.escape(text).replace("\n", "<br>")


def _escape_chat(text: str) -> str:
    # 문단 사이의 빈 줄(\n\n)은 그대로 두고, 문단 "안"의 문장 사이에만
    # 줄바꿈을 추가한다 (다음 글자가 공백이 아닌 경우 = 같은 문단이 이어지는 경우).
    text = re.sub(rf"({_SENTENCE_END}) (?=\S)", r"\1\n", text)
    return html_lib.escape(text)


def _change_color(change: str) -> str:
    # 국내 증시 관례: 상승=빨강, 하락=파랑
    if change.strip().startswith("-"):
        return "var(--down)"
    if change.strip().startswith("+"):
        return "var(--up)"
    return "var(--sub)"


def _sentiment_badge(sentiment: str) -> str:
    color = {
        "상승": "var(--up)",
        "하락": "var(--down)",
    }.get(sentiment, "var(--sub)")
    return f'<span class="badge" style="background:{color}">{_escape(sentiment)}</span>'


def _placeholder_panel(panel_id: str, message: str) -> str:
    return f"""
  <div class="tab-panel" id="panel-{panel_id}">
    <div class="panel-content">
      <div class="card placeholder-msg">{message}</div>
    </div>
  </div>"""


def _render_morning_panel(morning: dict | None) -> tuple[str, str]:
    """(패널 HTML, 모달 HTML) 튜플을 반환. morning이 없으면 준비중 표시."""
    if morning is None:
        return _placeholder_panel("morning", "개장 전 브리핑은 아직 준비 중입니다."), ""

    briefing = MarketBriefing.model_validate(morning)

    stats_html = "\n".join(
        f"""
        <div class="stat">
          <div class="stat-label">{_escape(s.label)}</div>
          <div class="stat-value">{_escape(s.value)}</div>
          <div class="stat-change" style="color:{_change_color(s.change)}">{_escape(s.change)}</div>
        </div>"""
        for s in briefing.key_stats
    )

    sections_html = "\n".join(
        f"""
        <section class="card">
          <h2><span class="num">{i+1}</span>{_escape(SECTIONS[i]["title"])}</h2>
          <p>{_escape(s.content)}</p>
        </section>"""
        for i, s in enumerate(briefing.sections)
    )

    panel = f"""
  <div class="tab-panel active" id="panel-morning">
    <div class="hero">
      <div class="hero-inner">
        {_sentiment_badge(briefing.sentiment)}
        <div class="hero-headline">{_escape(briefing.headline)}</div>
        <div class="stats">
          {stats_html}
        </div>
      </div>
    </div>

    <div class="summary-btn-wrap">
      <button class="summary-btn" onclick="document.getElementById('summaryModal').classList.add('open')">브리핑 요약하기</button>
    </div>

    <main>
      {sections_html}
    </main>
  </div>"""

    modal = f"""
  <div class="modal-overlay" id="summaryModal">
    <div class="modal-box">
      <div class="modal-header">
        <h3>브리핑 요약</h3>
        <button class="modal-close" onclick="document.getElementById('summaryModal').classList.remove('open')">&times;</button>
      </div>
      <div class="modal-body">
        <p class="chat-text" id="chatSummaryText">{_escape_chat(briefing.chat_summary)}</p>
      </div>
      <div class="modal-footer">
        <button class="copy-btn" id="copyBtn-chatSummaryText" onclick="copyText('chatSummaryText')">누르면 복사됩니다</button>
      </div>
    </div>
  </div>"""

    return panel, modal


def _render_lunch_panel(lunch: dict | None) -> str:
    if lunch is None:
        return _placeholder_panel("lunch", "점심시간 브리핑은 아직 준비 중입니다.")

    briefing = LunchBriefing.model_validate(lunch)

    return f"""
  <div class="tab-panel" id="panel-lunch">
    <div class="panel-content">
      <div class="card">
        <p class="chat-text" id="lunchText">{_escape_chat(briefing.text)}</p>
      </div>
      <div class="summary-btn-wrap" style="padding:0; margin-top:12px;">
        <button class="copy-btn" id="copyBtn-lunchText" onclick="copyText('lunchText')">누르면 복사됩니다</button>
      </div>
    </div>
  </div>"""


def _render_close_panel(close: dict | None) -> str:
    if close is None:
        return _placeholder_panel("close", "시장마감 브리핑은 아직 준비 중입니다.")

    briefing = CloseBriefing.model_validate(close)

    return f"""
  <div class="tab-panel" id="panel-close">
    <div class="panel-content">
      <div class="card">
        <p class="chat-text" id="closeText">{_escape_chat(briefing.text)}</p>
      </div>
      <div class="summary-btn-wrap" style="padding:0; margin-top:12px;">
        <button class="copy-btn" id="copyBtn-closeText" onclick="copyText('closeText')">누르면 복사됩니다</button>
      </div>
    </div>
  </div>"""


def render_html(state: dict, generated_date) -> str:
    date_str = generated_date.strftime("%Y년 %m월 %d일")
    weekday_kr = ["월", "화", "수", "목", "금", "토", "일"][generated_date.weekday()]

    morning_panel, morning_modal = _render_morning_panel(state.get("morning"))
    lunch_panel = _render_lunch_panel(state.get("lunch"))
    close_panel = _render_close_panel(state.get("close"))

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>오늘의 시황 브리핑</title>
<style>
  :root {{
    --bg: #f2f4f7;
    --card-bg: #ffffff;
    --text: #16181d;
    --sub: #6b7280;
    --accent: #2563eb;
    --border: #e5e7eb;
    --up: #d64545;
    --down: #2f6fed;
    --hero-bg-from: #14172b;
    --hero-bg-to: #262b4a;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 0 0 64px;
    background: var(--bg);
    color: var(--text);
    font-family: "Pretendard", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
    line-height: 1.65;
  }}
  .topbar {{
    background: #ffffff;
    border-bottom: 1px solid var(--border);
    padding: 14px 16px;
  }}
  .topbar-inner {{
    max-width: 720px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 700;
    font-size: 1.05rem;
  }}
  .topbar-inner .dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--accent);
    display: inline-block;
  }}
  .hero-header {{
    background: linear-gradient(135deg, var(--hero-bg-from), var(--hero-bg-to));
    color: #fff;
    padding: 20px 0 0;
  }}
  .hero-header-inner {{
    max-width: 720px;
    margin: 0 auto;
    padding: 0 16px;
  }}
  .hero {{
    background: linear-gradient(135deg, var(--hero-bg-from), var(--hero-bg-to));
    color: #fff;
    padding: 20px 16px 28px;
  }}
  .hero-inner {{
    max-width: 720px;
    margin: 0 auto;
  }}
  .hero-date {{
    color: #a7adc7;
    font-size: 0.85rem;
    margin-bottom: 14px;
  }}
  .tabbar {{
    display: flex;
    gap: 6px;
    margin-top: 4px;
  }}
  .tab-btn {{
    flex: 1;
    padding: 11px 8px;
    border: none;
    border-radius: 10px 10px 0 0;
    background: rgba(255,255,255,0.06);
    color: #a7adc7;
    font-size: 0.88rem;
    font-weight: 700;
    cursor: pointer;
  }}
  .tab-btn.active {{
    background: var(--bg);
    color: var(--text);
  }}
  .tab-panel {{
    display: none;
  }}
  .tab-panel.active {{
    display: block;
  }}
  .panel-content {{
    max-width: 720px;
    margin: 24px auto 0;
    padding: 0 16px;
  }}
  .placeholder-msg {{
    text-align: center;
    color: var(--sub);
    padding: 48px 22px;
  }}
  .hero-headline {{
    font-size: 1.35rem;
    font-weight: 700;
    line-height: 1.5;
    margin: 0 0 16px;
  }}
  .badge {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 14px;
  }}
  .stats {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(96px, 1fr));
    gap: 10px;
    margin-top: 4px;
  }}
  .stat {{
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 10px;
    padding: 10px 12px;
  }}
  .stat-label {{
    font-size: 0.75rem;
    color: #a7adc7;
    margin-bottom: 4px;
  }}
  .stat-value {{
    font-size: 0.95rem;
    font-weight: 700;
  }}
  .stat-change {{
    font-size: 0.8rem;
    font-weight: 600;
    margin-top: 2px;
  }}
  main {{
    max-width: 720px;
    margin: 24px auto 0;
    padding: 0 16px;
    display: flex;
    flex-direction: column;
    gap: 14px;
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
  .card p br {{
    content: "";
    display: block;
    margin-top: 0.55em;
  }}
  footer {{
    max-width: 720px;
    margin: 32px auto 0;
    padding: 0 16px;
    color: var(--sub);
    font-size: 0.8rem;
    text-align: center;
  }}
  .summary-btn-wrap {{
    max-width: 720px;
    margin: 18px auto 0;
    padding: 0 16px;
  }}
  .summary-btn {{
    width: 100%;
    padding: 13px 16px;
    border: none;
    border-radius: 10px;
    background: var(--accent);
    color: #fff;
    font-size: 0.95rem;
    font-weight: 700;
    cursor: pointer;
  }}
  .summary-btn:hover {{
    filter: brightness(1.08);
  }}
  .modal-overlay {{
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(15, 17, 26, 0.55);
    z-index: 50;
    padding: 20px;
    align-items: center;
    justify-content: center;
  }}
  .modal-overlay.open {{
    display: flex;
  }}
  .modal-box {{
    background: var(--card-bg);
    border-radius: 14px;
    max-width: 520px;
    width: 100%;
    max-height: 84vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }}
  .modal-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 18px;
    border-bottom: 1px solid var(--border);
  }}
  .modal-header h3 {{
    margin: 0;
    font-size: 1rem;
  }}
  .modal-close {{
    border: none;
    background: none;
    font-size: 1.3rem;
    line-height: 1;
    cursor: pointer;
    color: var(--sub);
    padding: 4px;
  }}
  .modal-body {{
    padding: 18px;
    overflow-y: auto;
  }}
  .chat-text {{
    white-space: pre-wrap;
    font-size: 0.92rem;
    color: #222;
    margin: 0;
  }}
  .modal-footer {{
    padding: 14px 18px;
    border-top: 1px solid var(--border);
  }}
  .copy-btn {{
    width: 100%;
    padding: 12px;
    border: none;
    border-radius: 10px;
    background: var(--accent);
    color: #fff;
    font-size: 0.92rem;
    font-weight: 700;
    cursor: pointer;
  }}
  .copy-btn.copied {{
    background: var(--up);
  }}
</style>
</head>
<body>
  <div class="topbar">
    <div class="topbar-inner"><span class="dot"></span>주식 시장 브리핑</div>
  </div>

  <div class="hero-header">
    <div class="hero-header-inner">
      <div class="hero-date">{date_str} ({weekday_kr})</div>
      <div class="tabbar">
        <button class="tab-btn active" id="tabbtn-morning" onclick="switchTab('morning')">개장 전 브리핑</button>
        <button class="tab-btn" id="tabbtn-lunch" onclick="switchTab('lunch')">점심시간</button>
        <button class="tab-btn" id="tabbtn-close" onclick="switchTab('close')">시장마감</button>
      </div>
    </div>
  </div>
{morning_panel}
{lunch_panel}
{close_panel}

  <footer>
    이 페이지는 매일 자동으로 수집·생성됩니다. 투자 판단의 참고용이며, 투자 조언이 아닙니다.
  </footer>
{morning_modal}

  <script>
    function switchTab(name) {{
      ['morning', 'lunch', 'close'].forEach(function(n) {{
        document.getElementById('panel-' + n).classList.toggle('active', n === name);
        document.getElementById('tabbtn-' + n).classList.toggle('active', n === name);
      }});
    }}
    function copyText(elementId) {{
      var text = document.getElementById(elementId).innerText;
      var btn = document.getElementById('copyBtn-' + elementId);
      function showCopied() {{
        btn.textContent = '복사됐습니다!';
        btn.classList.add('copied');
        setTimeout(function() {{
          btn.textContent = '누르면 복사됩니다';
          btn.classList.remove('copied');
        }}, 1500);
      }}
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(text).then(showCopied);
      }} else {{
        var ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        showCopied();
      }}
    }}
    var modalEl = document.getElementById('summaryModal');
    if (modalEl) {{
      modalEl.addEventListener('click', function(e) {{
        if (e.target === this) this.classList.remove('open');
      }});
    }}
  </script>
</body>
</html>
"""
