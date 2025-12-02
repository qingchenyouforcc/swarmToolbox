import json
import re
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from playwright.sync_api import sync_playwright

EN_URL = "https://en.neurosama.info/wiki/Main_Page"
ZH_URL = "https://zh.neurosama.info/wiki/%E9%A6%96%E9%A1%B5"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_en_schedule():
    # 嘗試直接 requests 拿 HTML
    r = requests.get(EN_URL, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # 若抓不到內容就用 Playwright（以防是動態載入）
    if not soup.select(".schedule-list li"):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(EN_URL, timeout=60000)
            html = page.content()
            browser.close()
            soup = BeautifulSoup(html, "html.parser")

    items = soup.select(".schedule-list li")
    data = []
    for li in items:
        week = li.select_one(".schedule-week")
        date = li.select_one(".schedule-date")
        title = li.select_one(".schedule-title")
        time = li.select_one(".time")
        data.append({
            "weekday": week.get_text(strip=True) if week else None,
            "date": date.get_text(strip=True) if date else None,
            "title": title.get_text(strip=True) if title else None,
            "time": time.get_text(strip=True) if time else None
        })
    return data

def fetch_zh_schedule():
    r = requests.get(ZH_URL, headers=HEADERS, timeout=15)
    r.raise_for_status()
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")

    node = soup.find(string=lambda s: isinstance(s, str) and "本周预告" in s)
    if not node:
        return []
    root = node.parent

    stop_words = {"Neuro新闻", "NeuroNews", "最新条目"}
    lines = []
    for sib in root.next_siblings:
        if isinstance(sib, NavigableString):
            t = sib.strip()
            if t and t not in stop_words:
                lines.append(t)
        elif isinstance(sib, Tag):
            txt = sib.get_text(strip=True)
            if txt in stop_words:
                break
            for s in sib.stripped_strings:
                lines.append(s.strip())

    WEEKDAY = re.compile(r"^周[一二三四五六日天]$")
    DATE = re.compile(r"^\d{1,2}月\d{1,2}日$")
    TIME = re.compile(r"^\d{2}:\d{2}\s*UTC\+8$")
    END_HINT = re.compile(r"^日期均为|^日期均為")

    events = []
    cur_week, cur_date = None, None
    i = 0
    while i < len(lines):
        t = lines[i]
        if END_HINT.search(t):
            break
        if WEEKDAY.match(t):
            cur_week = t
        elif DATE.match(t):
            cur_date = t
        else:
            title = t
            time_str = None
            if i + 1 < len(lines) and TIME.match(lines[i + 1]):
                time_str = lines[i + 1]
                i += 1
            if cur_week and cur_date:
                events.append({
                    "weekday": cur_week,
                    "date": cur_date,
                    "title": title,
                    "time": time_str
                })
        i += 1
    return events

def main():
    zh = fetch_zh_schedule()
    with open("zh_schedule.json", "w", encoding="utf-8") as f:
        json.dump(zh, f, ensure_ascii=False, indent=2)

    en = fetch_en_schedule()
    with open("en_schedule.json", "w", encoding="utf-8") as f:
        json.dump(en, f, ensure_ascii=False, indent=2)

    print("✅ 抓取完成")

if __name__ == "__main__":
    main()
