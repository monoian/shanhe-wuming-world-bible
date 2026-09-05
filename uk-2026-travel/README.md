# IAN 英國 2026 實戰攻略

這是直接發布於 GitHub Pages 的靜態網站。固定行程依 `20260908英國(0904).pdf`；攻略查核日期為 2026/09/05。網頁本身已含所有文字，不需要載入 JSON 才能看到行程。

## 修改入口

| 要改什麼 | 編輯檔案 |
|---|---|
| 正式行程、每一段車程、飯店、自由時段、推薦方案、清單與飲食卡 | `assets/itinerary.json` |
| 景點六區攻略、官方來源、首頁三個重點提醒、待確認事項 | `assets/guide.json` |
| HTML 結構與共用頁面版型 | `tools/build_site.py` |
| 所有樣式與手機版面 | `assets/styles.css` |
| 計算、Tab、日期導向、勾選與複製互動 | `assets/app.js` |

**不要直接修改產生的 HTML**。修改 JSON／版型後，執行：

```bash
python3 tools/build_site.py
python3 tools/verify_site.py
node tools/test_time.js
```

將資料來源與重新產生的 HTML 一起提交。沒有框架、CDN、Leaflet、Overpass、動態整頁重寫或 runtime JSON fetch。HTML 的 `data-*` 僅帶入該頁互動需要的資料；同一頁只有一份 `app.js`。

`guide.json` 的 `sources` 統一管理來源 URL；每個攻略用來源 ID 引用。新增景點必須提供 `must`（恰好三項）、`info`、`routes`、`photo`、`buy`、`risks`、`sources` 與 Maps 地名。商品與場次沒有確認時直接寫不確定，不補造店家／票券資訊。

## 自由時間資料與規則

- 每個 `days[].free` 引用 `freeModes`，最多依序白天、夜間、機場。每一頁共用一份表單。
- `freeModes` 的起訖與地點都是情境推估；沒有自由活動時設 `disabled: true`。前台不顯示虛假的零長度時段。
- `options` 的 `out`、`visit`、`back` 分別是保守去程、活動、回程分鐘。最低時間等於三者總和；一般散步已在活動與回程內，**不能再把回程重複加到表單緩衝**。
- 可用時間 = 集合時間 − 現在時間 − 使用者額外緩衝。選項再以包含往返的最低時間比較。
- 餘裕 15 分以上為可以；不足 15 分／接近關門為很趕；不足最低時間或超出營業為不建議。球道、票券等未確認時另列「時間夠・先確認」。
- `steps` 可指定某一站在出發後第幾分鐘完成，以及當日開／關門。`24:00` 可作關門邊界；不拿今天營業表保證翌日可用。
- 巴士的 `departures`、`checkin`、`visit` 共同驗證能趕上班次、遊程結束、回飯店與緩衝。沒有能完成整趟的班次直接顯示「來不及」。
- 跨午夜必須明選當日／翌日；負數一律歸零，不自動加 24 小時。輸入改變時舊結果失效，須重新計算。
- 真正「現在」使用 `Europe/London`。旅行前預填情境時間；不同旅行日不悄悄帶入今天的時間。

## 預覽與發布

可用一般靜態伺服器：

```bash
python3 -m http.server 8080
```

也可用零依賴 Node 預覽（接受 Work Mode 預覽的 host／port 參數）：

```bash
npm run dev -- --host 0.0.0.0 --port 4173 --strictPort
```

沒有 npm 依賴需要下載。`package.json` 只提供便利指令；GitHub Pages 直接使用已提交 HTML。

本次備份分支：`backup-uk-travel-before-rebuild-20260905`。備份起點：`0f1aa11fb007d8f44d7059c57fb646a06bdf5b64`；遠端備份已在修改前建立。舊版完整保留在該分支，不再混放到新版目錄。

發布只提交 `uk-2026-travel/`，不得改動同庫其他網站。提交訊息：`Rebuild UK travel site as practical field guide`。

## 驗證與限制

詳見 `QA.md`。清單只存在使用者當前瀏覽器的 localStorage，無跨裝置同步。網站沒有 service worker；已載入頁面可閱讀，首次開頁與地圖仍需網路。不能把瀏覽器快取視為完整離線保證。

照片：`assets/images/great-court.webp`，956×720，約 105 KiB。Andy Li / CC0；來源連結同時列於照片說明。圖片使用原生 lazy loading，沒有遠端字型。
