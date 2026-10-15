#!/usr/bin/env node
/** Generate Univacco-style decision deck from curated public-news issue database.
 * Usage: node scripts/monthly.js --month 2026-10 --preview
 * or:    node scripts/monthly.js --month last
 */
const fs=require('fs'),path=require('path');
const pptxgen=require('pptxgenjs');
// Use OpenAI slide helpers in authoring; CI fallback only when they are not installed.
let slideHelpers;try{slideHelpers=require('/home/oai/skills/slides/pptxgenjs_helpers')}catch(_){slideHelpers={svgToDataUri:(s)=>'data:image/svg+xml;base64,'+Buffer.from(s).toString('base64'),warnIfSlideHasOverlaps:()=>{},warnIfSlideElementsOutOfBounds:()=>{}}}
const {svgToDataUri,warnIfSlideHasOverlaps,warnIfSlideElementsOutOfBounds}=slideHelpers;
const root=path.resolve(__dirname,'..'),database=path.join(root,'data/issues.json');
const data=JSON.parse(fs.readFileSync(database,'utf8'));
function timeTaipei(){return new Date(new Date().toLocaleString('en-US',{timeZone:'Asia/Taipei'}))}
function defaultMonth(){let d=timeTaipei(); d.setDate(1);d.setMonth(d.getMonth()-1);return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')}
const argv=process.argv.slice(2), idx=argv.indexOf('--month'),month=idx>=0&&argv[idx+1]&&argv[idx+1]!=='last'?argv[idx+1]:defaultMonth(),preview=argv.includes('--preview');
if(!/^20\d\d-(0[1-9]|1[0-2])$/.test(month))throw Error('Need YYYY-MM month');
const filtered=data.editions.filter(e=>(e.published||'').slice(0,7)===month).sort((a,b)=>b.published.localeCompare(a.published));
const allNews=filtered.flatMap(x=>x.news||[]); const seen=new Set();let news=allNews.filter(n=>{let k=(n.title||'').toLowerCase().replace(/\W/g,'');if(seen.has(k))return false;seen.add(k);return true});
const latest=filtered[0]||data.editions[0]||{};const comps=latest.competitors||[];const actions=latest.actions||[];const focus=latest.lesson||{};
const src=(n)=>n&&n.url?n.url:'https://www.labelsandlabeling.com/';
const pp=new pptxgen();pp.layout='LAYOUT_WIDE';pp.author='印刷與燙金箔技術情報中心';pp.subject='公開產業情報、技術應用、品保與研發決策';pp.title=`${month} 燙金箔技術情報${preview?'期中試刊':'月報'}`;pp.lang='zh-TW';pp.company='Univacco Technology Inc.';pp.theme={headFontFace:'Microsoft JhengHei',bodyFontFace:'Microsoft JhengHei',lang:'zh-TW'};
const S=pp.ShapeType, C={b:'146EFF',d:'000082',black:'16213B',gray:'657188',pale:'F0F6FF',bg:'FFFFFF',line:'DFE8F6',warning:'C67524',green:'0B8975'};const W=13.333333,H=7.5;
const coverPath=path.join(root,'assets/univacco_cover_background.png'),whiteLogo=path.join(root,'assets/univacco_white_logo.png');
const add=(s,t,x,y,w,h,size=16,extra={})=>{s.addText(String(t||''),{x,y,w,h,fontFace:'Microsoft JhengHei',fontSize:size,color:C.black,margin:0,breakLine:false,fit:'shrink',valign:'mid',...extra})};
const rounded=(s,x,y,w,h,fill='FFFFFF',line='E4EBF4',radius=0.09)=>{s.addShape(S.roundRect,{x,y,w,h,rectRadius:radius,line:{color:line,width:.6},fill:{color:fill},radius})};
const bar=(s,x,y,w,h,fill=C.b)=>s.addShape(S.rect,{x,y,w,h,line:{color:fill,transparency:100},fill:{color:fill}});
const uIcon=svgToDataUri(`<svg xmlns="http://www.w3.org/2000/svg" width="90" height="90" viewBox="0 0 90 90"><path d="M0 0H90V42C90 70 71 89 45 89 19 89 0 70 0 42Z" fill="#146EFF"/></svg>`);
let slides=0;
function base(title,conclusion,section='MONTHLY TECHNOLOGY INTELLIGENCE'){
  slides++;let s=pp.addSlide();s.background={color:'FFFFFF'};
  bar(s,.35,.37,.08,.55);
  add(s,title,.58,.36,12.0,.44,26,{bold:true,color:C.b});
  add(s,conclusion,.59,.97,12.0,.46,18,{bold:true,color:C.black});
  s.addShape(S.line,{x:.59,y:1.52,w:12.05,h:0,line:{color:'DCE7F4',width:1.0}});
  add(s,section.toUpperCase(),.57,7.09,3.6,.16,8,{color:C.gray,charSpacing:1.5});
  add(s,`${slides}  © 2026 Univacco Technology Inc. All rights reserved.`,.57,7.31,6.1,.15,8,{color:C.gray});
  s.addImage({data:uIcon,x:12.78,y:7.00,w:.31,h:.31});
  return s
}
function action(s,label,y=6.54){rounded(s,.58,y,12.2,.4,'F0F6FF','F0F6FF');add(s,label,.74,y+.07,11.85,.25,12.8,{bold:true,color:'1358B7'});}
function note(s,urls){if(typeof s.addNotes==='function')s.addNotes('[Sources]\n'+[...new Set(urls.filter(Boolean))].join('\n'))}
function textCard(s,x,y,w,h,top,bottom,color=C.b){rounded(s,x,y,w,h);bar(s,x+.16,y+.16,.05,.35,color);add(s,top,x+.31,y+.16,w-.46,.31,15,{bold:true,color:C.black});add(s,bottom,x+.3,y+.6,w-.5,h-.76,12.8,{color:'53627B',valign:'top',breakLine:false})}
function bullet(s,str,x,y,w,h,color=C.black,size=13){add(s,'• '+str,x,y,w,h,size,{color,breakLine:false,valign:'top'})}
function sourceTag(s,t,x,y,w){rounded(s,x,y,w,.32,'F0F6FF','F0F6FF');add(s,t,x+.1,y+.04,w-.18,.23,10.5,{color:C.b,bold:true})}
// 1: cover based on company's supplied style asset (not a generic template)
{let s=pp.addSlide();slides++;s.addImage({path:coverPath,x:0,y:0,w:W,h:H});s.addImage({path:whiteLogo,x:10.45,y:.37,w:2.35,h:.365});
 add(s,'印刷產業與燙金箔\n技術情報月度報告',6.00,1.45,6.45,1.65,31,{color:'FFFFFF',bold:true,breakLine:false});
 add(s,preview?'2026 年 10 月｜截至 10/15 期中試刊':`${month}｜月度情報分析`,6.04,3.42,6.25,.41,20,{color:'F6FBFF',bold:true});
 add(s,'產業技術 × 競品觀察 × 材料與品質驗證',6.04,4.15,6.4,.36,16,{color:'DCEBFF'});
 add(s,'公開資料研究｜非產品規格或正式對外保證',6.04,5.90,6.5,.26,11.5,{color:'DCEBFF'});
 note(s,['https://www.kurz-world.com/en/solutions/embellishment-machines/']);}
// 2 executive summary
{const s=base('管理摘要｜三項值得採取的技術行動','數位裝飾、UV 固化與量測標準化，正在重新定義轉印品質的驗證需求');
 textCard(s,.61,1.84,3.9,2.6,'01｜數位印後裝飾','傳統與數位冷燙的接著模式可能不同，應避免直接套用單一材料規格。');
 textCard(s,4.72,1.84,3.9,2.6,'02｜UV 油墨與固化','新的油墨訴求提高固化與遷移管控重要性，需將客戶製程條件納入測試。');
 textCard(s,8.83,1.84,3.9,2.6,'03｜客戶使用檢驗','從固定位置的 L*／色差／缺陷判定，建立與實際印刷效果的關聯性。');
 sourceTag(s,`Ta｜${news.length} 則本期公開資訊`,.65,4.86,3.45);sourceTag(s,'Target｜建立可重複驗證方法',4.33,4.86,4.2);sourceTag(s,`Time｜${month} 研究期`,8.75,4.86,3.4);
 action(s,'👉 決策：同意以「UV相容性、檢驗一致性、被印材資料庫」作為 3 項優先可行性評估。');
 note(s,news.slice(0,6).map(src));}
// 3 technical news
{const s=base('技術發展｜數位冷燙與 UV 油墨','材料端的離型、接著與光學檢測，必須結合客戶上膠及固化條件評估');
 const a=news.find(x=>x.id==='n-xaar'||(x.brand||'').toLowerCase().includes('xaar')),b=news.find(x=>x.id==='n-sun'||(x.brand||'').toLowerCase().includes('sun chemical'));
 textCard(s,.62,1.83,6.0,3.35,a?'數位裝飾｜'+a.brand:'數位冷燙（技術背景）','設備可整合到現有印刷／後加工線，應注意印刷速度與數位上膠的轉印窗口。');
 textCard(s,6.80,1.83,5.9,3.35,b?'UV 柔版油墨｜'+b.brand:'UV 油墨與固化（技術背景）','快速固化與低遷移是產品訴求，但對特定燙箔與被印材的相容性仍須實驗證實。');
 bullet(s,'技術驗證：上膠量 × 固化條件 × 速度，量測轉印率／L*／缺陷比例。',.82,5.45,11.6,.47,C.black,14);
 action(s,'👉 行動：研發與品保先制定跨材料、跨設備的冷燙應用參數測試卡。');note(s,[src(a),src(b)]);}
// 4 QC standardization
{const s=base('品質系統｜量測位置與判定一致性','從單點數值合格，升級為「版面位置化」的亮度與缺陷檢驗');
 textCard(s,.63,1.82,6.8,2.05,'印刷品質管理的參考方向',news.some(x=>x.brand==='Techkon')?'本期 Techkon ChromaQA 7.5 報導涉及指定量測位置、色彩標準及品質報表。':'技術背景：指定量測位置、統一色彩標準及品質報表，是實際使用結果比較的必要基礎。');
 textCard(s,7.58,1.82,5.1,2.05,'材料供應商可借鏡的方向','固定照明與視角，保留位置資訊，區分 ΔE、亮度與缺陷面積。');
 add(s,'建議驗證流程（尚非既有公司作業）',.72,4.06,8.2,.34,15,{bold:true,color:C.b});
 const labels=['樣品與圖案編碼','固定量測位置','影像／L*／目視盲測','一致性與客戶效果'];const xs=[.67,3.85,7.05,10.08],ww=[2.9,2.9,2.8,2.62];
 labels.forEach((v,i)=>{rounded(s,xs[i],4.65,ww[i],.85,i%2===0?'F0F6FF':'FFFFFF','CCDDF5');add(s,`${i+1}. ${v}`,xs[i]+.16,4.92,ww[i]-.25,.26,13,{bold:true,color:'1C4784'});if(i<3)add(s,'→',xs[i]+ww[i]+.12,4.82,.32,.32,23,{color:C.b})});
 action(s,'👉 行動：至少 30 件代表樣品進行目視盲測與位置化量測，確認漏判與誤判情形。');note(s,news.filter(x=>x.brand==='Techkon').map(src));}
// 5 competitor
{const s=base('競爭廠商｜比較公開技術布局，而非猜測性能','以公開產品／設備資訊建立競品比較基準，避免將舊資料當作本月新公告');
 const list=comps.slice(0,3);let ys=[1.83,3.12,4.41];
 list.forEach((c,i)=>{rounded(s,.65,ys[i],12.02,1.11,i===0?'F4F8FF':'FFFFFF','E0EAF6');add(s,c.name,.87,ys[i]+.20,3.11,.27,16,{bold:true,color:i===0?C.b:C.black});add(s,c.focus,4.01,ys[i]+.13,4.00,.44,13,{color:'3F587C'});add(s,c.gap,8.10,ys[i]+.09,4.20,.63,12,{color:'48648B',valign:'mid'});add(s,c.updated,1.02,ys[i]+.69,3.0,.19,10.5,{color:C.gray});});
 add(s,'資料時窗：KURZ 近期展會內容為 2026/09；API／KATANI 以官網產品頁作為背景資料，非本週新品。',.80,5.81,12.0,.37,11,{color:C.gray});
 action(s,'👉 決策：以「應用條件 × 轉印效果 × 檢驗方法」建立競品技術對照表，不做未經測試的優劣判定。');note(s,comps.map(x=>x.news_url).concat(comps.map(x=>x.url)));}
// 6 substrate and environment
{const s=base('材料與法規｜新被印材帶來相容性與證據需求','永續包裝相關材料發展，不能直接當作燙金箔可回收性或法規符合的證明');
 const n1=news.find(x=>x.id==='n-innovia'),n2=news.find(x=>x.id==='n-ppg');
 textCard(s,.64,1.83,5.94,2.45,'金屬化 BOPP 包裝薄膜','阻隔型金屬化薄膜與轉印裝飾箔用途不同，避免直接替換或簡化比較。');
 textCard(s,6.77,1.83,5.94,2.45,'生質來源合成紙','新型表面塗層／填料可能改變界面潤濕與轉印性，應建立應用條件資料。');
 rounded(s,.65,4.65,12.02,.98,'F8FAFE','E8EEF7');add(s,'區分三種證據',.87,4.76,2.35,.25,15,{bold:true,color:C.b});
 add(s,'化學符合性  ≠  實際回收性  ≠  材料轉印適用性',3.2,4.74,8.85,.27,16,{bold:true,color:'285080'});
 action(s,'👉 行動：針對新基材先測表面能、粗糙度、耐熱與轉印率；環保宣稱另由合規證據支持。');note(s,[src(n1),src(n2),'https://environment.ec.europa.eu/news/new-eu-rules-packaging-enter-application-2026-08-11_en']);}
// 7 decision plans
{const s=base('建議工作清單｜先做 3 項小型驗證','先取得可重複的使用證據，再決定是否納入正式規格或新產品專案');
 const y0=1.83,rows=actions.slice(0,3);const col=[.67,2.86,6.36,9.44,12.67];
 bar(s,.65,y0,12.02,.48,'EAF2FF');[['議題',.89,1.83],['技術／實驗方法',3.04,3.15],['協作單位',6.60,2.7],['驗收證據',9.66,2.65]].forEach(([x,xx,w])=>add(s,x,xx,y0+.1,w,.25,13,{bold:true,color:'134D91'}));
 rows.forEach((a,i)=>{const y=y0+.48+i*1.24;if(i%2===0)bar(s,.65,y,12.02,1.24,'F9FBFE');add(s,`${a.priority}｜${a.title}`, .87,y+.15,2.03,.88,13,{bold:true,color:'213E6A',valign:'top'});add(s,a.method,3.04,y+.12,3.18,.95,12.2,{color:'4B617D',valign:'top'});add(s,a.owner,6.59,y+.16,2.59,.8,12,{color:'416086',valign:'top'});add(s,a.accept,9.64,y+.12,2.72,.93,12.2,{color:'405D83',valign:'top'});s.addShape(S.line,{x:.69,y:y+1.22,w:11.92,h:0,line:{color:'E5EBF4',width:.8}})});
 add(s,'※ 本表為建議優先序及驗收方式，尚未指派正式責任人與完成期限。',.78,6.11,11.7,.28,10.7,{color:C.gray});
 action(s,'👉 決策：請主管確認三個驗證主題的優先序、可用樣品與負責窗口。');note(s,news.slice(0,4).map(src));}
// 8 teaching topic + roadmap
{const s=base('持續學習｜技術情報需轉換成驗證能力','技術教學應聚焦客戶真正看見的轉印品質與材料檢驗的關聯性');
 rounded(s,.63,1.83,7.55,3.62,'F4F8FF','E1EBFA');add(s,'本期教學主題',.9,2.03,6.2,.29,14,{color:C.b,bold:true});add(s,focus.title||'冷燙工藝與品質',.9,2.47,6.85,.77,22,{bold:true,color:'1A406C'});
 add(s,focus.principle||'',.9,3.47,6.85,1.1,14,{color:'536783',valign:'top'});
 rounded(s,8.38,1.83,4.31,3.62);add(s,'每週標準學習循環',8.64,2.08,3.75,.33,17,{bold:true,color:C.b});
 ['了解技術原理與工藝條件','解讀新聞與競品應用','建立可能的品質風險假設','以 DOE / MSA / 使用測試驗證'].forEach((t,i)=>{add(s,`${i+1}. ${t}`,8.66,2.65+i*.51,3.73,.34,13,{color:'455F82'})});
 add(s,'建議 30 天內：完成一份應用條件對照表與至少一項試驗設計。',.85,5.78,11.8,.4,13.5,{bold:true,color:C.b});
 action(s,'👉 行動：每週保留 20 分鐘技術學習與案例討論，月底回顧可驗證的改善成果。');note(s,[src(news[0])]);}
// 9 source appendix
{const s=base('附錄｜來源、範圍與使用限制','研究資料僅供技術研習及管理討論，不能取代產品驗證或正式法規判定','SOURCES & EVIDENCE BOUNDARIES');
 const sources=[...new Map(news.map(n=>[n.url,n])).values()].slice(0,6);const urls=[];
 sources.forEach((n,i)=>{const y=1.78+i*.54;add(s,`${i+1}. ${n.source}｜${n.title}`, .75,y,11.90,.34,12.3,{color:i%2?C.black:'174E93'});urls.push(n.url)});
 add(s,'判讀原則：供應商宣稱 ≠ 獨立量測結果；應用風險為分析假設，需實際印刷驗證。',.74,5.38,11.86,.49,13.6,{bold:true,color:'1B4677'});
 add(s,`資料範圍：${preview?'2026/10/01–10/15':month}｜網站公開資訊；報告之建議項目尚非公司核准工作事項。`,.74,5.96,11.85,.36,11.5,{color:C.gray});
 action(s,'👉 決策：發布對外資料前由業務、品保及法規窗口再核對來源與聲明依據。');note(s,urls.concat(comps.map(c=>c.url)));}
// Full slide validation: expected intentional overlaps for text on framed cards.
for(const sl of pp._slides){warnIfSlideElementsOutOfBounds(sl,pp); /* frame and text are intentionally layered; run shape-overlap diagnostics in QA mode */ if(process.env.VERIFY_PPT_OVERLAPS==='1')warnIfSlideHasOverlaps(sl,pp);}
const filename=`${month}_技術情報_${preview?'期中試刊':'月報'}_V1.pptx`;const output=path.join(root,'reports',filename);
fs.mkdirSync(path.dirname(output),{recursive:true});
pp.writeFile({fileName:output}).then(()=>{
  console.log('WROTE',output,'slides',slides);
  if(!preview){data.reports=data.reports||[];const title=`${month} 技術情報｜月度管理報告`;const entry={title,file:`reports/${filename}`,status:'月報','date':new Date().toISOString().slice(0,10),month};data.reports=data.reports.filter(x=>x.month!==month||x.status==='期中試刊');data.reports.unshift(entry);fs.writeFileSync(database,JSON.stringify(data,null,2));}
}).catch(e=>{console.error(e);process.exit(1)});
