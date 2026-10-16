#!/usr/bin/env python3
"""Free weekly public-news intake, offline preliminary translation, NO paid API.
Only saves candidates for manual fact-checking. Never publishes candidate stories.
"""
import argparse
import hashlib
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
TZ = ZoneInfo("Asia/Taipei")
FEEDS = [
    ("hot stamping foil printing labels packaging", "熱燙與裝飾"),
    ("cold foil transfer flexographic printing", "冷燙與應用"),
    ("digital embellishment digital foil printing", "數位燙金"),
    ("LEONHARD KURZ foil embossing labels", "競品動態"),
    ("API Foilmakers transfer foil packaging", "競品動態"),
    ("KATANI foil hot stamping", "競品動態"),
    ("flexographic UV ink inline inspection label press", "印刷與品質"),
]
EXCLUDE = ("football", "hockey", "bitcoin", "stock market", "court", "police",
           "investment advice", "gold price", "real estate", "print on demand",
           "printing services in", "high-quality printing solutions in",
           "providing fast and high-quality", "local printing company")
RELEVANCE = ("foil", "stamping", "embellish", "flexo", "label press",
             "printing press", "printing equipment", "holograph", "gravure",
             "offset", "uv ink", "uv-cur", "print inspection", "laminat",
             "packaging material", "substrate", "metallic", "packaging printing",
             "printing technology", "printing industry", "printbar",
             "printing ink", "colour management", "color management",
             "label market", "label printing", "label finisher", "press line", "printing solutions")
MAX_ITEMS = 14


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def week_range():
    now = datetime.now(TZ).date()
    monday = now - timedelta(days=now.weekday())
    start, end = monday - timedelta(days=7), monday - timedelta(days=1)
    week = start.isocalendar()
    return start, end, f"{week.year}-W{week.week:02d}"


def clean(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()


def valid_title(title):
    low = title.lower()
    if len(title) < 18 or any(bad in low for bad in EXCLUDE):
        return False
    return any(term in low for term in RELEVANCE)


def get_rss(start, end):
    records, errors = [], []
    for keyword, category in FEEDS:
        query = f"{keyword} after:{start.isoformat()} before:{(end + timedelta(days=1)).isoformat()}"
        endpoint = "https://news.google.com/rss/search?" + urllib.parse.urlencode(
            {"q": query, "hl": "en-US", "gl": "US", "ceid": "US:en"})
        try:
            req = urllib.request.Request(endpoint, headers={"User-Agent": "Mozilla/5.0 FoilTechNewsReview/2.0"})
            with urllib.request.urlopen(req, timeout=18) as resp:
                rss = ET.fromstring(resp.read(2_500_000))
            for node in rss.findall(".//item")[:25]:
                title, url = clean(node.findtext("title")), clean(node.findtext("link"))
                if not url.startswith("https://"):
                    continue
                publisher = node.find("source")
                source = clean(publisher.text) if publisher is not None else "Google News RSS"
                if " - " in title:
                    left, right = title.rsplit(" - ", 1)
                    if right.casefold() == source.casefold():
                        title = left.strip()
                if not valid_title(title):
                    continue
                try:
                    dt = parsedate_to_datetime(clean(node.findtext("pubDate"))).astimezone(TZ).date()
                except Exception:
                    continue
                if not start <= dt <= end:
                    continue
                records.append({
                    "id": "rss-" + hashlib.sha256(url.encode("utf-8")).hexdigest()[:14],
                    "date": dt.isoformat(),
                    "category": category,
                    "source": source or "Google News RSS",
                    "url": url,
                    "original_title": title,
                    "title_zh": "",
                    "translation_status": "待機器翻譯",
                    "review_status": "待人工查核原文",
                    "verification": "RSS 僅為新聞候選；尚未核對原文、技術數據或來源宣稱。",
                })
        except Exception as exc:
            errors.append(f"{keyword}: {str(exc)[:140]}")
    unique = {}
    for item in sorted(records, key=lambda n: n["date"], reverse=True):
        key = re.sub(r"[^a-z0-9]", "", item["original_title"].casefold())
        if key not in unique:
            unique[key] = item
    return list(unique.values())[:MAX_ITEMS], errors


class OfflineTranslator:
    """Argos Translate en->zh, OpenCC Simplified->Traditional/Taiwan.
    If model download fails, leave English visible as original, not a fake translation.
    """

    def __init__(self):
        self.ready = False
        self.error = ""
        try:
            import argostranslate.package as pkg
            import argostranslate.translate as translate
            from opencc import OpenCC
            self.translate = translate
            self.converter = OpenCC("s2twp")
            installed = translate.get_installed_languages()
            if not any(getattr(x, "code", "") == "en" for x in installed) or \
                    not any(getattr(x, "code", "") == "zh" for x in installed):
                package = next((x for x in pkg.get_available_packages()
                                if x.from_code == "en" and x.to_code == "zh"), None)
                if package is None:
                    raise RuntimeError("no downloadable en-to-zh Argos model")
                pkg.install_from_path(package.download())
            self.ready = True
        except Exception as exc:
            self.error = str(exc)[:180]

    def convert(self, text):
        if not self.ready:
            return ""
        try:
            chinese = self.converter.convert(self.translate.translate(text, "en", "zh"))
            if len(re.findall(r"[\u3400-\u9fff]", chinese)) < 3:
                return ""
            return clean(chinese)
        except Exception:
            return ""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", help="Do not modify website data")
    p.add_argument("--no-translate", action="store_true", help="Collect headlines without downloading a translation model")
    args = p.parse_args()
    start, end, week_id = week_range()
    items, errors = get_rss(start, end)
    translator = None
    if items and not args.no_translate:
        translator = OfflineTranslator()
        if translator.error:
            print("WARN translation unavailable:", translator.error, file=sys.stderr)
        for item in items:
            chinese = translator.convert(item["original_title"])
            if chinese:
                item["title_zh"] = chinese
                item["translation_status"] = "免費離線機器初譯｜待人工校對"
            else:
                item["translation_status"] = "翻譯暫不可用｜保留英文原標題"
    else:
        for item in items:
            item["translation_status"] = "待人工翻譯"
    payload = {
        "week_id": week_id,
        "period": f"{start.isoformat()}–{end.isoformat()}",
        "collected_at": datetime.now(TZ).isoformat(timespec="seconds"),
        "status": "RSS 候選待審｜非正式週報",
        "source_method": "Google News RSS (free)",
        "translation_method": "Argos Translate en-zh + OpenCC 繁體中文（若模型可用）",
        "items": items,
        "errors": errors,
        "review_steps": [
            "逐一開啟原始報導，確認日期、產品型號和可核實事實",
            "校對繁體中文標題，去除不相關或重複消息",
            "利用 ChatGPT 撰寫重點結論、工程風險及品質驗證提案",
            "人工審核並以 GitHub Actions 匯入正式週報",
        ],
    }
    translated = sum(bool(n["title_zh"]) for n in items)
    print(f"COLLECTED {week_id}: {len(items)} candidates, {translated} machine translations, {len(errors)} feed errors")
    if args.dry_run:
        print("DRY RUN: no files changed")
    else:
        write(ROOT / "data/pending_news.json", payload)
        print("Saved data/pending_news.json; official site editions unchanged")
    for error in errors:
        print("WARN RSS:", error, file=sys.stderr)


if __name__ == "__main__":
    main()
