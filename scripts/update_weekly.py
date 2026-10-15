#!/usr/bin/env python3
"""Public news RSS + pre-authored lesson. Never fabricate article details.
Run on GitHub Actions Monday 08:30 Asia/Taipei after publication workflow setup.
"""
import json, os, re, sys, argparse, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
BASE=Path(__file__).resolve().parents[1]
TZ=ZoneInfo('Asia/Taipei')
KEYWORDS=['hot stamping foil printing labels packaging', 'cold foil embellishment flexo print','digital foil stamping printing','LEONHARD KURZ packaging foil', 'API Foilmakers API Transfer foil','KATANI hot stamping foil','printing packaging ink inspection flexo']
CLASS=['燙金技術','冷燙與應用','數位燙金','競品動態','競品動態','競品動態','印刷技術']
EXCLUDE=['court','police','crime','football','hockey','bitcoin','gold price','stock market']

def read_json(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def write_json(path,obj):Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def roundup(t):return re.sub(r'\s+',' ',t or '').strip()
def get_feeds(start,end):
  records=[];failed=[]
  for keyword, category in zip(KEYWORDS,CLASS):
    # Google News RSS: independent headlines, not independently verified technical text.
    q=f'{keyword} after:{start.isoformat()} before:{(end+timedelta(days=1)).isoformat()}'
    path='https://news.google.com/rss/search?'+urllib.parse.urlencode({'q':q,'hl':'en-US','gl':'US','ceid':'US:en'})
    try:
      req=urllib.request.Request(path,headers={'User-Agent':'Mozilla/5.0 (compatible; FoilIntelligenceBot/1.0)'})
      with urllib.request.urlopen(req,timeout=17) as r:data=r.read(3_000_000)
      rss=ET.fromstring(data)
      for node in rss.findall('.//item')[:28]:
        title=roundup(node.findtext('title')); link=roundup(node.findtext('link'))
        if not title or not link.startswith('https://'):continue
        low=title.lower()
        if any(w in low for w in EXCLUDE):continue
        pub=roundup(node.findtext('pubDate'))
        try:dt=parsedate_to_datetime(pub).astimezone(TZ).date()
        except Exception:continue
        if not start<=dt<=end:continue
        source_node=node.find('source'); src=(source_node.text or '').strip() if source_node is not None else 'Google News RSS'
        if ' - ' in title:
          left,right=title.rsplit(' - ',1)
          if right.strip().lower()==src.lower():title=left
        records.append({'id':re.sub(r'[^a-z0-9]','',str(abs(hash(link)))),'date':dt.isoformat(),'category':category,'type':'RSS 標題｜尚待核實全文','level':'medium','brand':src or '公開新聞','title':title,'source':src or 'Google News RSS','url':link,'description':'這是自動擷取的公開新聞標題與日期；尚未完整查核報導內容，請點閱原始來源。','impact':'待查核技術內容與應用條件後，再判斷對燙金箔材料、印刷或品質管理的具體影響。','verification':'僅標題、日期和來源資訊已自動擷取；不得視為完整技術分析。'})
    except Exception as ex:failed.append(f'{keyword}: {str(ex)[:100]}')
  unique={}
  for x in sorted(records,key=lambda x:x['date'],reverse=True):
    k=re.sub(r'\W+','',x['title']).lower()
    if k not in unique:unique[k]=x
  return list(unique.values())[:12],failed

def lesson_of_week(lessons,number):
  x=lessons[number%len(lessons)]
  return {'number':number%len(lessons)+1,'title':x['title'],'subtitle':'每週系統化學習｜公開教材延伸與應用假設','duration':'約 20–30 分鐘','principle':x['principle'],'params':x['params'],'case':x['case'],'verify':x['verify'],'quiz':[{'q':'這堂課最需要控制的兩個印刷參數是什麼？','a':'請從上列關鍵參數中選擇兩項並說明原因；依不同工藝答案可能不同。'},{'q':'遇到客戶使用異常，能直接斷定是燙金箔配方造成嗎？','a':'不能；須控制材料、被印材、設備及量測條件，並透過適當的試驗確認。'},{'q':'本堂最適合建立哪一種記錄？','a':x['verify']}]}

def actions_of_week(l,week_id):
  defaults=[('高','設計材料／客戶印刷條件對照測試','材料與印刷條件可能有交互作用','固定兩種代表基材與材料批次，分層比較關鍵機台參數；量測轉印率、亮度、缺陷比例。','建立代表條件測試矩陣並重複確認，形成對外應用條件說明。','研發＋品保＋製程技術'),('高','檢驗方式與客戶效果的一致性評估','單一物性數據可能不足以解釋使用表現','選 ≥30 件正常與異常樣品，固定視角／量測位置並執行盲測；比較屬性判定與數值指標。','完成一致性分析與漏判／誤判評估，提出方法改善建議。','品保＋研發'),('中','技術情報與產品應用需求對照','新工藝可能帶來新型材料 CTQ','將本週技術對照預期應用情境、材料 CTQ、競品功能及可取得的驗證資源。','完成一頁式技術需求與驗證優先順序建議。','研發＋業務＋品保')]
  return [{'id':f'{week_id}-A{j+1}','priority':level,'title':title,'basis':l['title'],'hypothesis':h,'method':m,'accept':accept,'owner':owner,'state':'建議評估｜未經公司內部批准'} for j,(level,title,h,m,accept,owner) in enumerate(defaults)]

def main():
  parser=argparse.ArgumentParser(description='Weekly public news refresh')
  parser.add_argument('--dry-run',action='store_true',help='Fetch and validate without changing site data')
  args=parser.parse_args()
  now=datetime.now(TZ)
  # On Monday use last complete calendar week; on other days also choose preceding completed week.
  this_monday=now.date()-timedelta(days=now.weekday());start=this_monday-timedelta(days=7);end=this_monday-timedelta(days=1)
  week_id=f'{start.isocalendar().year}-W{start.isocalendar().week:02d}'
  # Editorial gate: RSS entries are candidates, never publish unverified English headlines.
  candidates, failed = get_feeds(start,end)
  pending_path=BASE/'data/pending_news.json'
  pending={'week_id':week_id,'period':f'{start.isoformat()}–{end.isoformat()}','status':'候選待審｜未發布正式週報','review_required':['核對原始全文及日期','翻譯繁體中文標題','撰寫新聞重點結論','區分來源事實與技術推論','補上品保與研發建議'],'items':candidates,'feed_errors':failed}
  print(f'{("DRY RUN" if args.dry_run else "PENDING REVIEW")}: {week_id}; {len(candidates)} RSS candidates; {len(failed)} errors; no unreviewed news published')
  if not args.dry_run:
    write_json(pending_path,pending)
  for e in failed:print('WARN:',e,file=sys.stderr)
  return
  path=BASE/'data/issues.json';data=read_json(path)
  if any(x.get('id')==week_id for x in data['editions']):print('Already published:',week_id);return
  news,failed=get_feeds(start,end)
  curriculum=read_json(BASE/'data/curriculum.json')
  l=lesson_of_week(curriculum,len(data['editions']))
  all_competitors=(data['editions'][0].get('competitors') or [])
  comp=[]
  for c in all_competitors:
    clone=dict(c)
    found=[x for x in news if any(v.lower() in (x['title']+' '+x['brand']).lower() for v in {'LEONHARD KURZ':['KURZ'], 'API Foilmakers / API Transfer':['API Foilmakers','API Transfer'], 'KATANI':['Katani']}.get(c['name'],[c['name']]))]
    clone.update(new_this_week=bool(found),status='待查核新聞標題' if found else '本週未納入新公告',updated=end.isoformat())
    if found:clone['detail']='本週 RSS 找到相關標題：'+found[0]['title']+'。尚待查核原文。';clone['news_url']=found[0]['url']
    comp.append(clone)
  status='自動快訊｜新聞原文待人工審核'
  if failed:status+='｜部分來源抓取失敗'
  intro='本期以公開 RSS 新聞標題整理為基礎；完整技術細節、競爭廠商宣稱及產品相容性均待查證。'
  if not news:intro='本週未取得符合條件的可用 RSS 新聞；仍照常更新技術教學與改善提案。'
  issue={'id':week_id,'period':f'{start.strftime("%Y/%m/%d")}–{end.strftime("%m/%d")}','published':now.date().isoformat(),'title':f'{week_id}｜每週技術快訊','status':status,'headline':f'{l["title"]}｜從技術新聞看產品應用','summary':intro,'news':news,'competitors':comp,'actions':actions_of_week(l,week_id),'lesson':l,'background':data['editions'][0].get('background',[]),'editorial':'本週自動抓取新聞標題僅供追蹤，未經全文核實；請勿作為技術或公司聲明。','refresh_errors':failed}
  if args.dry_run:
    print(f'DRY RUN ONLY: {week_id}, {len(news)} RSS titles, {len(failed)} feed errors; no files changed')
  else:
    data['editions'].insert(0,issue);data['generated']=now.date().isoformat();write_json(path,data)
    print(f'Published {week_id}: {len(news)} titles, {len(failed)} feed errors')
  for x in failed:print('WARN:',x,file=sys.stderr)
if __name__=='__main__':main()
