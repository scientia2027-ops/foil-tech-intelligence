#!/usr/bin/env python3
"""After GitHub Pages deployment, verify the visible JSON and downloadable PPTX bytes."""
import json
import os
import sys
import time
import urllib.request
from urllib.parse import quote

site=(os.environ.get("PAGES_URL") or "https://scientia2027-ops.github.io/foil-tech-intelligence/").rstrip("/")+"/"
expected=json.load(open("data/issues.json",encoding="utf-8"))["reports"][0]
last=None
for n in range(9):
    try:
        with urllib.request.urlopen(site+"data/issues.json?smoke="+str(int(time.time())),timeout=22) as r:
            info=json.loads(r.read(1000000))
        match=next((x for x in info.get("reports",[]) if x.get("file")==expected["file"]),None)
        if not match:raise ValueError("new report not yet listed on public Pages JSON")
        public=site+quote(match["file"],safe="/")
        req=urllib.request.Request(public,headers={"Range":"bytes=0-3","User-Agent":"FoilMonthlyDownloadCheck/1.0"})
        with urllib.request.urlopen(req,timeout=35) as r:
            signature=r.read(4)
            status=r.status
        if status not in (200,206) or signature!=b"PK\x03\x04":
            raise ValueError(f"download unexpected: HTTP {status}; bytes {signature!r}")
        print("PUBLIC_PPT_DOWNLOAD_OK:",public,"HTTP",status,"signature",signature.hex())
        sys.exit(0)
    except Exception as exc:
        last=str(exc)
        print(f"public download smoke test attempt {n+1}/9: {last}",file=sys.stderr)
        time.sleep(8)
raise SystemExit("PUBLIC_PPT_DOWNLOAD_FAILED: "+str(last))
