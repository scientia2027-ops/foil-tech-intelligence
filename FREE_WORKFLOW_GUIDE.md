# 免費方案 A｜技術情報每週審稿與每月自動簡報

## 不需要 OpenAI API
- 每週一台灣時間 **08:30**：GitHub Actions 使用 Google News RSS 擷取上一個完整週的公開新聞候選。
- 初譯：Argos Translate 免費離線模型（英文→中文），以 OpenCC 轉成繁體中文。這是**機器初譯**，不是專業審稿。若模型下載或轉譯失敗，保留英文原文及狀態，蒐集不會中斷。
- 候選存入 `data/pending_news.json`，**不會自動加進正式歷史週報**。
- 每月 1 日台灣時間 **09:30**：GitHub Actions 無需任何付費 API，彙整網站 `data/issues.json` 已發布且經過審核的內容，生成 PowerPoint。若該月沒有已審核來源，簡報標示資料不足。

## 每週只需做一次的人工步驟
1. 開啟 [週報審稿工作台](https://scientia2027-ops.github.io/foil-tech-intelligence/editor.html)。
2. 按「讀取候選新聞」，將候選 JSON 與工作台內的 ChatGPT 提示詞交給 ChatGPT。
3. 使用 ChatGPT 協助查核公開原始報導、翻譯繁中、撰寫新聞重點／工程分析／競品比較與改善方案。**先人工核對真正原始資料，勿只靠標題；不要貼公司未授權公開資料。**
4. 將生成的 JSON 貼回工作台。確認來源、新聞日期、數據與內容，將 `approved_by_editor` 設為 `true`。
5. 由工作台下載 `reviewed_import.json`。
6. 在 GitHub [儲存庫 data 目錄](https://github.com/scientia2027-ops/foil-tech-intelligence/tree/main/data) 上傳同名檔案 `data/reviewed_import.json`（若已存在則編輯或覆寫）。
7. 到 [Import reviewed weekly intelligence](https://github.com/scientia2027-ops/foil-tech-intelligence/actions/workflows/import-reviewed.yml) 選擇 **Run workflow**。
8. 等完成後到 [網站歷史週報](https://scientia2027-ops.github.io/foil-tech-intelligence/#archive) 確認新增期別。

## 核對清單
- 正確日期、原文直接 HTTPS 連結、廠商／設備名稱與事實說明。
- 每則繁中標題、重點結論、技術摘要、對材料與品質的影響，以及尚待驗證的限制。
- KURZ、API、KATANI 無可靠新消息時應標註未見新公告，不能捏造產品性能。
- 品質改善提案是建議，**不是公司已核准的標準或工作指派**。
- JSON 範本在 [data/reviewed_import.example.json](https://github.com/scientia2027-ops/foil-tech-intelligence/blob/main/data/reviewed_import.example.json)。

## 注意
ChatGPT 訂閱不等於 API 額度；此備援版的 GitHub 週報蒐集與 PPT 生成不會呼叫付費 OpenAI API。
免費翻譯模型需從公開伺服器下載，因此無法保證每次翻譯成功；原文和錯誤狀態會保留。
