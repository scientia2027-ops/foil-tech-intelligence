# 印刷產業與燙金箔技術情報中心

> 繁體中文網站／公開技術週報／競品雷達／品保研發改善提案／岱稜風格月度 PPT 產生器。
>
> **版本：V1.1（GitHub 發布檢查版）；試刊資料截至 2026-10-15。** 未完成網站部署前，檔案不會出現在可分享的網址。

## 1. 專案內容

| 檔案或資料夾 | 用途 |
|---|---|
| `index.html` | 網站首頁：內含一份離線備援資料，可在下載後直接開啟。 |
| `assets/style.css`、`assets/app.js` | 響應式網站樣式、新聞篩選、競品與改善提案。 |
| `data/issues.json` | 每週週報資料庫（含查核來源、技術教學與行動項目）。 |
| `data/curriculum.json` | 16 週的預先撰寫技術教學主題。 |
| `scripts/update_weekly.py` | 每週更新公開 RSS 標題，輪替技術教材並建議驗證題目。 |
| `scripts/embed_data.py` | 每次更新後刷新首頁內嵌資料，確保離線仍可開啟。 |
| `scripts/monthly.js` | 讀取週報，產生 16:9、岱稜藍色風格、含 U 形頁腳識別的 PPT。 |
| `.github/workflows/weekly-news.yml` | 每週一台灣時間 08:30 執行新聞更新。 |
| `.github/workflows/monthly-report.yml` | 每月首日台灣時間 09:30 產生上個月的 PPT。 |
| `.github/workflows/deploy-site.yml` | 首次發布網站，並在每週/月排程完成後重新部署 GitHub Pages。 |
| `reports/` | 管理簡報歷史下載。 |

### 現有示範內容

- 2026/10/13–10/14 的 6 則已查核公開資訊，含原文連結與證據界線。
- KURZ、API Transfer / API Foilmakers、KATANI 競品追蹤。
- 冷燙轉印技術深度教學與小測驗。
- 三項品保／研發驗證提案（均為建議，**不是公司正式指派**）。
- 2026 年 10 月期中試刊管理簡報（9 張投影片）。

## 2. 將網站公開上線：GitHub Pages

若希望任何人透過網址都能閱讀，推薦將整個資料夾發布為 GitHub Pages 靜態網站。**發布需要擁有者登入 GitHub 並建立或連結存放庫；光下載 ZIP 並不代表網站已上線。**

1. 登入 GitHub，建立**公開（Public）**儲存庫，例如 `foil-tech-intelligence`；初始化時先不要勾選 README、.gitignore 或 License，避免上傳時產生同名檔案。
2. 將 ZIP 解壓後，**上傳其內部的檔案與資料夾到儲存庫根目錄，不要額外保留外層資料夾**。必須在根目錄看到 `index.html`、`assets/`、`data/`、`scripts/`、`reports/`、`.github/` 與 `package.json` **全部保留內部目錄結構**後推送到預設分支 `main`。注意上傳工具須顯示並包含隱藏資料夾 `.github`。
3. 在儲存庫 **Settings → Pages → Build and deployment → Source** 選擇 **GitHub Actions**。專案已包含 `Publish public foil intelligence site`，不需使用「Deploy from a branch」；這樣每週由工作流程提交的資料也能重新部署。
4. 等 GitHub Pages 建置完成，網站通常可以由以下模式存取：`https://<GitHub 使用者名稱>.github.io/foil-tech-intelligence/`。**這只是網址規則範例，並不是已存在的網址。**
5. 在 **Actions** 分頁確認 `Weekly foil intelligence refresh`、`Monthly technical decision deck` 與 `Publish public foil intelligence site` 三個工作流程正常啟用。網站發布工作流程會在推送程式碼、每週更新完成或月報完成後部署網站。**週報與月報工作流程需要 `contents: write`**；若儲存庫政策阻止寫入，須由管理員在 **Settings → Actions → General → Workflow permissions** 調整成允許寫入。
6. 首次可從 GitHub Actions 手動執行 `Publish public foil intelligence site`，確認網站能開啟；先手動執行 `Weekly foil intelligence refresh`，將 `dry_run` 保持 `true`，確認 RSS 擷取與程式執行的紀錄（**此模式不更新週報也不發布**）。等到預定週一正式排程時，確認其自動執行、修改 `data/issues.json` 並接續觸發網站部署。如必須提前手動發布，才把 `dry_run` 設為 `false`；在週一以外的時間執行會擷取「上個完整週」，不一定是當週。

> **公開性提醒：** Public GitHub Pages 網址不是「只有知道連結的人才能看」的權限保護，搜尋引擎或其他人也可能看到。絕對不要上傳尚未授權的公司內部產品參數、試驗數據、客戶客訴、未公開競品情報或個資。若需指定人員才可看，應改用有登入驗證的受控網站。

## 3. 每週會自動更新哪些項目？

**正式發布後，週一 08:30 台灣時間預定執行：**

1. 從 Google News RSS 依日期和關鍵字取得公開新聞標題、發布日、連結（網路服務可能變動／失效）。
2. 將標題放進網站新聞區。**機器抓取僅代表取得 RSS 項目，不等於完整核實新聞全文**；新項目明確標記「RSS 標題／待查核」，不捏造新聞技術細節。
3. 從預先撰寫的 16 週教材中輪替每週的主題，包含原理、製程參數、案例、驗證及測驗。
4. 依技術主題生成三項**通用**驗證建議；如要轉換為真正的岱稜內部決策，必須先由授權人員確認數據、責任人及規格。
5. GitHub Actions 在非 dry-run 執行時自動提交資料；完成後由 `Publish public foil intelligence site` 透過官方 `actions/deploy-pages` 重新部署網站。不能只靠來源分支部署，因為 GitHub 官方指出 `GITHUB_TOKEN` 自動提交**不會觸發**分支式 Pages 重建。若 RSS 抓取失敗，網站保留明確的限制提示，不會杜撰新聞。

**限制：** 此公開版沒有串接 ChatGPT 任務內容，也不會自動複製 ChatGPT 每週產出的深入分析。完整的「新聞逐則深度解析／競品技術比較／具體改善」應先人工查核再寫入 `data/issues.json`，或後續另行設定有安全審核的專業分析流程。現有 GitHub Actions 在未設定任何 API 金鑰的情況下，仍可更新標題、教材與改善提案。

**重要：** 若網站尚未完成 GitHub Pages 部署，排程不會在此下載檔案上運作。網站必須有正式 GitHub 儲存庫、Actions 權限與 Pages 發布設定。

## 4. 月度 PPT 自動產生

每月首日（09:30 台灣時間）預計生成前一個月的簡報，寫入 `reports/` 並顯示於網站「管理簡報」。目前已提供 `reports/2026-10_技術情報_期中試刊_V1.pptx`，屬 2026/10/15 **期中試刊**，不能當作完整 10 月月報。

可手動在 GitHub Actions 的 `Monthly technical decision deck` 輸入月份，例如 `2026-10`，或在安裝 Node.js 後自行執行：

```bash
npm install
node scripts/monthly.js --month 2026-10
python scripts/embed_data.py
```

PPT 使用公司提供的視覺樣式參考：企業藍 `#146EFF`、16:9、封面品牌漸層影像、內容頁右下角 U 形識別、主管決策與行動導向。**此版本以程式重新套用母版風格，不是直接在原始 PPT 母片內新增投影片**；若需百分之百沿用 PowerPoint 原生母片，可另以原始母版進行人工套版。

**月報品質限制：** 未經人工核實的 RSS 新聞不得直接作為確定結論。自動簡報的來源頁及分析說明應在主管正式使用前逐項檢查。

## 5. 如何人工新增一則完整週報？

編輯 `data/issues.json` 最新一期的 `news` 陣列，每則消息應保留：

- `date`、`title`、`source`、`url`：真實發布日期、新聞名稱及原始連結。
- `type`：區分新聞事實／供應商宣稱／媒體報導／RSS 待查核。
- `description`：經過核實的摘要。
- `impact`：對材料、品保、研發或應用技術的分析推論。
- `verification`：分析的限制與尚待驗證的問題。

修改後執行 `python scripts/embed_data.py`，再提交到 GitHub。

## 6. 自動更新是否保證準時？

GitHub 的排程可能延遲或因儲存庫權限、服務異常、長期無活動等因素暫停；RSS 供應商也可能更動介面。建議每月檢查三個工作流程是否成功執行。若需要企業級通知、審核與可用性保障，應另行部署伺服器、監控及正式的編輯／審核工作流程。

## 7. 資料來源與著作權

網站連結導向原始新聞，不鏡像或轉載完整付費文章、圖片或影片。已整理的新聞屬二次編輯的短篇摘要，不代表原文可商業再發布；公開前應尊重來源網站使用條款。網站素材與公司標誌僅供有權使用者的簡報／研究使用。

## 8. 首次上線確認清單（V1.1）

- [ ] GitHub 公開儲存庫預設分支為 `main`，根目錄**直接**看得到 `index.html`。
- [ ] `.github/workflows/` 內有三個 `.yml` 工作流程。
- [ ] Settings → Pages → Build and deployment → Source 為 **GitHub Actions**。
- [ ] Settings → Actions → General → Workflow permissions 允許 **Read and write permissions**（用於每週資料提交及月報產生）。
- [ ] Actions → `Publish public foil intelligence site` 成功；Settings → Pages 顯示網站網址。
- [ ] 公開網址可開啟，側邊選單正常，新聞連結與 PPT 下載正常。
- [ ] Actions → `Weekly foil intelligence refresh` → `Run workflow`，勾選 **dry_run=true**，驗證 log 中沒有程式錯誤。
- [ ] 第一個實際週一執行後，`data/issues.json` 增加新週次，Actions 再次成功部署，網站可看到新一期。

> GitHub 排程可能延遲；RSS 來源可能暫時無結果。dry-run 成功代表執行及擷取流程可運作，不保證下週一定有可用新聞。
