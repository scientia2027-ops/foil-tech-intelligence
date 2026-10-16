#!/usr/bin/env python3
"""Import a manually verified ChatGPT JSON edition; fail closed on incomplete claims."""
import argparse,json,re,sys
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
def zh(s,n=8):return len(re.findall(r"[\u3400-\u9fff]",str(s or "")))>=n
def check(doc,db):
    err=[];week=str(doc.get("id",""))
    if not re.fullmatch(r"20\d\d-W\d\d",week):err.append("id must be YYYY-Www")
    if not doc.get("approved_by_editor"):err.append("approved_by_editor must be true after human review")
    if not zh(doc.get("headline"),10):err.append("headline needs Traditional Chinese")
    if not zh(doc.get("summary"),20):err.append("summary too short")
    news=doc.get("news",[])
    if not isinstance(news,list) or not 1<=len(news)<=12:err.append("news needs 1-12 records")
    for i,n in enumerate(news if isinstance(news,list) else []):
        if not all(zh(n.get(k),lim) for k,lim in (("title",8),("takeaway",14),("description",22),("impact",15),("verification",12))):err.append(f"news[{i}] Chinese article fields incomplete")
        u=str(n.get("url",""))
        p=urlsplit(u)
        if p.scheme!="https" or not p.hostname or "google.com" in p.hostname:err.append(f"news[{i}] needs direct HTTPS original source")
        try:date.fromisoformat(n["date"])
        except Exception:err.append(f"news[{i}] needs YYYY-MM-DD date")
        if not n.get("source"):err.append(f"news[{i}] needs source")
    for j,a in enumerate(doc.get("actions",[])):
        if not zh(a.get("title"),4) or not zh(a.get("method"),12):err.append(f"actions[{j}] incomplete")
    return err
def main():
    p=argparse.ArgumentParser();p.add_argument("--input",default="data/reviewed_import.json");p.add_argument("--check",action="store_true");args=p.parse_args()
    src=ROOT/args.input
    if not src.exists():raise SystemExit("No reviewed JSON found: "+str(src))
    data=json.loads(src.read_text("utf8"));path=ROOT/"data/issues.json";db=json.loads(path.read_text("utf8"))
    errs=check(data,db)
    if errs:
        for e in errs:print("INVALID:",e,file=sys.stderr)
        raise SystemExit(1)
    edition={k:v for k,v in data.items() if k not in ("approved_by_editor","reviewer_notes")}
    edition["status"]="人工審核完成｜繁體中文深度解析";edition["review_status"]="human_approved"
    edition.setdefault("title",edition["id"]+"｜印刷與燙金箔技術週報")
    edition.setdefault("period","請參考新聞日期")
    edition.setdefault("published",date.today().isoformat())
    edition.setdefault("competitors",db["editions"][0].get("competitors",[]))
    edition.setdefault("actions",[])
    edition.setdefault("lesson",db["editions"][0].get("lesson"))
    edition.setdefault("background",[])
    for n in edition["news"]:
        n.setdefault("category","印刷與燙金技術")
        n.setdefault("brand",n.get("source","公開來源"))
        n.setdefault("type","已人工核對來源｜編輯分析")
        n.setdefault("level","medium")
    if args.check:print("CHECK_OK",edition["id"],len(edition["news"]));return
    db["editions"]=[e for e in db["editions"] if e.get("id")!=edition["id"]]
    db["editions"].insert(0,edition)
    db["generated"]=date.today().isoformat()
    path.write_text(json.dumps(db,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("IMPORTED",edition["id"],len(edition["news"]))
if __name__=="__main__":main()
