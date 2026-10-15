#!/usr/bin/env python3
"""Validate generated PowerPoint and its web database link using only stdlib."""
import json
import sys
import zipfile
import re
import xml.etree.ElementTree as ET
from pathlib import Path

root = Path(__file__).resolve().parents[1]
db = json.loads((root/"data/issues.json").read_text("utf-8"))
assert db.get("reports"), "No reports recorded in site database"
entry = db["reports"][0]
p = root / entry["file"]
assert p.is_file(), "PPT not present at " + str(p)
assert p.stat().st_size >= 30000, "PPT unexpectedly small"
assert p.read_bytes()[:4] == b"PK\x03\x04", "PPT not a ZIP-based Office file"
EMU = 914400
with zipfile.ZipFile(p) as z:
    assert z.testzip() is None, "Corrupt PPTX member"
    names = z.namelist()
    pages = sorted((n for n in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),key=lambda x:int(re.search(r"(\d+)\.xml$",x).group(1)))
    assert len(pages) >= 8, "PPT should have at least 8 slides"
    ns={"p":"http://schemas.openxmlformats.org/presentationml/2006/main",
        "a":"http://schemas.openxmlformats.org/drawingml/2006/main"}
    pr=ET.fromstring(z.read("ppt/presentation.xml"))
    size=pr.find("p:sldSz",ns)
    W=int(size.get("cx"));H=int(size.get("cy"))
    assert abs(W/H-16/9)<0.01, "Slide dimensions must be 16:9"
    violations=[]
    for name in pages:
        page=ET.fromstring(z.read(name))
        for node in page.findall(".//p:sp/p:spPr/a:xfrm",ns)+page.findall(".//p:pic/p:spPr/a:xfrm",ns):
            off=node.find("a:off",ns);ext=node.find("a:ext",ns)
            if off is None or ext is None:continue
            x=int(off.get("x"));y=int(off.get("y"));w=int(ext.get("cx"));h=int(ext.get("cy"))
            if x < -60000 or y < -60000 or x+w>W+60000 or y+h>H+60000:
                violations.append((name,round(x/EMU,2),round(y/EMU,2),round(w/EMU,2),round(h/EMU,2)))
    assert not violations, "Slide element(s) out of bounds: "+repr(violations[:10])
    texts=[]
    for slide in pages:
        part=ET.fromstring(z.read(slide))
        texts.extend((t.text or "") for t in part.findall(".//a:t",ns))
    assert any(("技術情報" in t or "燙金箔" in t) for t in texts),"Report missing title"
    if "測試" in entry.get("status",""):
        assert any("測試" in t for t in texts),"Test report must be visibly labeled as a test"
    assert any("ppt/notesSlides/notesSlide" in name for name in names), "Missing notes and source links"
print("VALIDATED_PPTX:",entry["file"],"bytes",p.stat().st_size,
      "slides",len(pages),"aspect","16:9","report_status",entry["status"],"sources/notes","present")
