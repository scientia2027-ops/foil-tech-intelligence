#!/usr/bin/env python3
"""No-key source diagnostics. Shows raw RSS counts without importing unverified news."""
import sys, urllib.request, urllib.parse, xml.etree.ElementTree as ET, re
from datetime import date,timedelta
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo
from update_weekly import FEEDS, EXCLUDE, RELEVANCE, valid_title, week_range, clean
start,end,week_id=week_range()
print("DIAGNOSTIC WEEK", week_id, start, end, flush=True)
all_count=0
for kw,category in FEEDS:
    q=f"{kw} after:{start.isoformat()} before:{(end+timedelta(days=1)).isoformat()}"
    url="https://news.google.com/rss/search?"+urllib.parse.urlencode({"q":q,"hl":"en-US","gl":"US","ceid":"US:en"})
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=18) as r:body=r.read(2000000)
        tree=ET.fromstring(body);raw=tree.findall(".//item")
        accepted=0;dates=0;relevant=0
        for item in raw[:60]:
            title=clean(item.findtext("title"));date_str=clean(item.findtext("pubDate"))
            try: d=parsedate_to_datetime(date_str).astimezone(ZoneInfo("Asia/Taipei")).date()
            except:continue
            if start<=d<=end:dates+=1
            if valid_title(title):relevant+=1
            if start<=d<=end and valid_title(title):accepted+=1
        all_count+=accepted
        print("QUERY",kw,"RAW",len(raw),"DURING_WEEK",dates,"RELEVANCE",relevant,"PASS",accepted,flush=True)
        for item in raw[:2]:
            print("SAMPLE",clean(item.findtext("title"))[:130],"@",clean(item.findtext("pubDate")),flush=True)
    except Exception as e:print("ERROR",kw,repr(e)[:200],flush=True)
print("DIAGNOSTIC TOTAL",all_count,flush=True)
