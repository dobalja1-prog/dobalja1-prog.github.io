from datetime import date

# 월요일=0, 화=1, ... 토=5, 일=6 (Python의 weekday() 기준)
SATURDAY = 5
SUNDAY = 6
MONDAY = 0


def is_run_day(today=None):
    """토요일, 일요일에는 실행하지 않는다."""
    today = today or date.today()
    return today.weekday() not in (SATURDAY, SUNDAY)


def get_lookback_days(today=None):
    """월요일이면 토·일 포함 3일치, 그 외 평일이면 1일치를 가져온다."""
    today = today or date.today()
    if today.weekday() == MONDAY:
        return 3
    return 1


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    from datetime import timedelta

    monday = date(2026, 8, 31)
    for i in range(7):
        d = monday + timedelta(days=i)
        요일 = ["월", "화", "수", "목", "금", "토", "일"][d.weekday()]
        print(f"{d} ({요일}) -> 실행:{is_run_day(d)} / 조회기간:{get_lookback_days(d)}일")
